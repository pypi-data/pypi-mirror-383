"""Unit tests for the in-memory workflow repository implementation."""

from __future__ import annotations
from datetime import UTC, datetime
from uuid import uuid4
import pytest
from orcheo.triggers.cron import CronTriggerConfig, CronTriggerState
from orcheo.triggers.webhook import WebhookTriggerConfig
from orcheo_backend.app.repository import (
    InMemoryWorkflowRepository,
    RepositoryError,
    VersionDiff,
    WorkflowNotFoundError,
    WorkflowRunNotFoundError,
    WorkflowVersionNotFoundError,
)


@pytest.fixture()
def repository() -> InMemoryWorkflowRepository:
    """Return a fresh repository instance for each test."""

    return InMemoryWorkflowRepository()


@pytest.mark.asyncio()
async def test_create_and_list_workflows(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Workflows can be created and listed with deep copies returned."""

    created = await repository.create_workflow(
        name="Test Flow",
        slug=None,
        description="Example workflow",
        tags=["alpha"],
        actor="tester",
    )

    workflows = await repository.list_workflows()
    assert len(workflows) == 1
    assert workflows[0].id == created.id
    assert workflows[0].slug == "test-flow"

    # Returned instances must be detached copies.
    workflows[0].name = "mutated"
    fresh = await repository.get_workflow(created.id)
    assert fresh.name == "Test Flow"


@pytest.mark.asyncio()
async def test_update_and_archive_workflow(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Updating a workflow touches each branch of metadata normalization."""

    created = await repository.create_workflow(
        name="Original",
        slug="custom-slug",
        description="Desc",
        tags=["a"],
        actor="author",
    )

    updated = await repository.update_workflow(
        created.id,
        name="Renamed",
        description="New desc",
        tags=["b"],
        is_archived=None,
        actor="editor",
    )
    assert updated.name == "Renamed"
    assert updated.description == "New desc"
    assert updated.tags == ["b"]
    assert updated.is_archived is False

    archived = await repository.archive_workflow(created.id, actor="editor")
    assert archived.is_archived is True

    unchanged = await repository.update_workflow(
        created.id,
        name=None,
        description=None,
        tags=["b"],
        is_archived=True,
        actor="editor",
    )
    assert unchanged.tags == ["b"]
    assert unchanged.is_archived is True
    # The most recent audit event should not include redundant metadata.
    assert unchanged.audit_log[-1].metadata == {}


@pytest.mark.asyncio()
async def test_update_missing_workflow(repository: InMemoryWorkflowRepository) -> None:
    """Updating a missing workflow raises an explicit error."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.update_workflow(
            uuid4(),
            name=None,
            description=None,
            tags=None,
            is_archived=None,
            actor="tester",
        )


@pytest.mark.asyncio()
async def test_version_management(repository: InMemoryWorkflowRepository) -> None:
    """Version CRUD supports numbering, listing, and retrieval."""

    workflow = await repository.create_workflow(
        name="Versioned",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )

    first = await repository.create_version(
        workflow.id,
        graph={"nodes": ["a"], "edges": []},
        metadata={"first": True},
        notes=None,
        created_by="author",
    )
    second = await repository.create_version(
        workflow.id,
        graph={"nodes": ["a", "b"], "edges": []},
        metadata={"first": False},
        notes="update",
        created_by="author",
    )

    versions = await repository.list_versions(workflow.id)
    assert [version.version for version in versions] == [1, 2]
    assert versions[0].id == first.id

    looked_up = await repository.get_version_by_number(workflow.id, 2)
    assert looked_up.id == second.id

    fetched = await repository.get_version(second.id)
    assert fetched.id == second.id

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_version_by_number(workflow.id, 3)

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_version_by_number(uuid4(), 1)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_version(uuid4())

    diff = await repository.diff_versions(workflow.id, 1, 2)
    assert isinstance(diff, VersionDiff)
    assert diff.base_version == 1
    assert diff.target_version == 2
    assert any('+    "b"' in line for line in diff.diff)


@pytest.mark.asyncio()
async def test_create_version_without_workflow(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Creating a version for an unknown workflow fails."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.create_version(
            uuid4(),
            graph={},
            metadata={},
            notes=None,
            created_by="actor",
        )


@pytest.mark.asyncio()
async def test_run_lifecycle(repository: InMemoryWorkflowRepository) -> None:
    """Runs can transition through success, failure, and cancellation."""

    workflow = await repository.create_workflow(
        name="Runnable",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    # Successful run path
    run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={"payload": True},
    )
    started = await repository.mark_run_started(run.id, actor="runner")
    assert started.status == "running"
    succeeded = await repository.mark_run_succeeded(
        run.id, actor="runner", output={"result": "ok"}
    )
    assert succeeded.status == "succeeded"
    assert succeeded.output_payload == {"result": "ok"}

    # Failed run path
    failed_run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={},
    )
    failed = await repository.mark_run_failed(
        failed_run.id, actor="runner", error="boom"
    )
    assert failed.status == "failed"
    assert failed.error == "boom"

    # Cancelled run path
    cancelled_run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={},
    )
    cancelled = await repository.mark_run_cancelled(
        cancelled_run.id, actor="runner", reason="stop"
    )
    assert cancelled.status == "cancelled"
    assert cancelled.error == "stop"

    runs = await repository.list_runs_for_workflow(workflow.id)
    assert {run.status for run in runs} == {"succeeded", "failed", "cancelled"}


@pytest.mark.asyncio()
async def test_run_error_paths(repository: InMemoryWorkflowRepository) -> None:
    """All run error branches raise the correct exceptions."""

    missing_workflow_id = uuid4()
    with pytest.raises(WorkflowNotFoundError):
        await repository.create_run(
            missing_workflow_id,
            workflow_version_id=uuid4(),
            triggered_by="actor",
            input_payload={},
        )

    workflow = await repository.create_workflow(
        name="Run Errors",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    _ = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.create_run(
            workflow.id,
            workflow_version_id=uuid4(),
            triggered_by="actor",
            input_payload={},
        )

    other_workflow = await repository.create_workflow(
        name="Other",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    mismatched_version = await repository.create_version(
        other_workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.create_run(
            workflow.id,
            workflow_version_id=mismatched_version.id,
            triggered_by="actor",
            input_payload={},
        )

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.get_run(uuid4())

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_started(uuid4(), actor="actor")

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_succeeded(uuid4(), actor="actor", output=None)

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_failed(uuid4(), actor="actor", error="err")

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_cancelled(uuid4(), actor="actor", reason=None)


@pytest.mark.asyncio()
async def test_create_run_with_cron_source_tracks_overlap(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron-sourced runs register overlap tracking even without stored state."""

    workflow = await repository.create_workflow(
        name="Cron Indexed",
        slug=None,
        description=None,
        tags=None,
        actor="cron",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="cron",
    )

    run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="cron",
        input_payload={},
    )
    assert repository._cron_run_index[run.id] == workflow.id

    await repository.mark_run_started(run.id, actor="cron")
    await repository.mark_run_succeeded(run.id, actor="cron", output=None)
    assert run.id not in repository._cron_run_index


@pytest.mark.asyncio()
async def test_list_entities_error_paths(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Listing versions or runs for unknown workflows surfaces not found errors."""

    missing_id = uuid4()
    with pytest.raises(WorkflowNotFoundError):
        await repository.list_versions(missing_id)

    with pytest.raises(WorkflowNotFoundError):
        await repository.list_runs_for_workflow(missing_id)


@pytest.mark.asyncio()
async def test_reset_clears_internal_state(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Reset removes all previously stored workflows, versions, and runs."""

    workflow = await repository.create_workflow(
        name="Reset",
        slug=None,
        description=None,
        tags=None,
        actor="actor",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="actor",
    )
    await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="actor",
        input_payload={},
    )

    await repository.reset()

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_workflow(workflow.id)


def test_repository_error_hierarchy() -> None:
    """Ensure repository-specific errors inherit from the common base."""

    assert issubclass(WorkflowNotFoundError, RepositoryError)
    assert issubclass(WorkflowVersionNotFoundError, RepositoryError)
    assert issubclass(WorkflowRunNotFoundError, RepositoryError)


@pytest.mark.asyncio()
async def test_get_latest_version_validation(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Latest version retrieval enforces workflow and version existence."""

    workflow = await repository.create_workflow(
        name="Latest", slug=None, description=None, tags=None, actor="tester"
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_latest_version(workflow.id)

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_latest_version(uuid4())

    version = await repository.create_version(
        workflow.id,
        graph={"nodes": []},
        metadata={},
        notes=None,
        created_by="tester",
    )
    latest = await repository.get_latest_version(workflow.id)
    assert latest.id == version.id
    repository._versions.pop(version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_latest_version(workflow.id)


@pytest.mark.asyncio()
async def test_webhook_configuration_requires_workflow(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Configuring a webhook for a missing workflow raises an error."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.configure_webhook_trigger(uuid4(), WebhookTriggerConfig())


@pytest.mark.asyncio()
async def test_webhook_configuration_roundtrip(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Webhook configuration persists and returns deep copies."""

    workflow = await repository.create_workflow(
        name="Webhook", slug=None, description=None, tags=None, actor="tester"
    )
    config = WebhookTriggerConfig(allowed_methods={"POST", "GET"})

    stored = await repository.configure_webhook_trigger(workflow.id, config)
    assert set(stored.allowed_methods) == {"POST", "GET"}

    fetched = await repository.get_webhook_trigger_config(workflow.id)
    assert fetched == stored


@pytest.mark.asyncio()
async def test_handle_webhook_trigger_missing_resources(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Webhook handling raises when workflow or versions are missing."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.handle_webhook_trigger(
            uuid4(),
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )

    workflow = await repository.create_workflow(
        name="Webhook Flow", slug=None, description=None, tags=None, actor="tester"
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )

    version = await repository.create_version(
        workflow.id,
        graph={"nodes": []},
        metadata={},
        notes=None,
        created_by="tester",
    )
    await repository.configure_webhook_trigger(workflow.id, WebhookTriggerConfig())

    repository._versions.pop(version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )


@pytest.mark.asyncio()
async def test_cron_trigger_configuration_and_dispatch(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron trigger configuration is persisted and schedules runs."""

    workflow = await repository.create_workflow(
        name="Cron Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    saved = await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 12 * * *", timezone="UTC"),
    )
    assert saved.expression == "0 12 * * *"

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    )
    assert len(runs) == 1
    run = runs[0]
    assert run.triggered_by == "cron"
    assert run.input_payload["scheduled_for"] == "2025-01-01T12:00:00+00:00"

    repeat = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    )
    assert repeat == []


@pytest.mark.asyncio()
async def test_cron_trigger_requires_existing_workflow(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron trigger helpers raise when the workflow is unknown."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.configure_cron_trigger(uuid4(), CronTriggerConfig())

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_cron_trigger_config(uuid4())


@pytest.mark.asyncio()
async def test_cron_trigger_overlap_guard(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron scheduler skips scheduling when an active run exists."""

    workflow = await repository.create_workflow(
        name="Overlap Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 9 * * *", timezone="UTC"),
    )

    first = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 9, 0, tzinfo=UTC)
    )
    assert len(first) == 1
    run_id = first[0].id

    skipped = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
    )
    assert skipped == []

    await repository.mark_run_started(run_id, actor="cron")
    await repository.mark_run_succeeded(run_id, actor="cron", output=None)

    next_runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 2, 9, 0, tzinfo=UTC)
    )
    assert len(next_runs) == 1


@pytest.mark.asyncio()
async def test_dispatch_due_cron_runs_handles_edge_cases(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron dispatcher gracefully skips invalid and incomplete state entries."""

    naive_now = datetime(2025, 1, 1, 11, 0)

    # Entry without a persisted workflow.
    repository._cron_states[uuid4()] = CronTriggerState()

    # Workflow without versions.
    workflow_without_versions = await repository.create_workflow(
        name="No Versions",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    repository._cron_states[workflow_without_versions.id] = CronTriggerState(
        CronTriggerConfig(expression="0 11 * * *", timezone="UTC")
    )

    # Workflow with a missing latest version object.
    workflow_missing_version = await repository.create_workflow(
        name="Missing Version",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    orphaned_version = await repository.create_version(
        workflow_missing_version.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )
    repository._versions.pop(orphaned_version.id)
    repository._cron_states[workflow_missing_version.id] = CronTriggerState(
        CronTriggerConfig(expression="0 11 * * *", timezone="UTC")
    )

    # Workflow that is not yet due.
    workflow_not_due = await repository.create_workflow(
        name="Not Due",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow_not_due.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )
    repository._cron_states[workflow_not_due.id] = CronTriggerState(
        CronTriggerConfig(expression="0 12 * * *", timezone="UTC")
    )

    runs = await repository.dispatch_due_cron_runs(now=naive_now)
    assert runs == []


@pytest.mark.asyncio()
async def test_dispatch_due_cron_runs_respects_overlap_without_creating_runs(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron dispatcher skips scheduling when overlap guard is active."""

    workflow = await repository.create_workflow(
        name="Guarded Cron",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 7 * * *", timezone="UTC"),
    )
    state = repository._cron_states[workflow.id]
    state.register_run(uuid4())

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 7, 0, tzinfo=UTC)
    )
    assert runs == []


@pytest.mark.asyncio()
async def test_cron_trigger_timezone_alignment(
    repository: InMemoryWorkflowRepository,
) -> None:
    """Cron scheduler respects configured timezones when dispatching."""

    workflow = await repository.create_workflow(
        name="TZ Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 9 * * *", timezone="America/Los_Angeles"),
    )

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 17, 0, tzinfo=UTC)
    )
    assert len(runs) == 1
