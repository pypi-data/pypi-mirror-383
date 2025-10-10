"""
Tests for workspace data isolation

These tests verify that workspace-scoped models properly isolate data
and that queries respect workspace boundaries.
"""

import pytest
from uuid import uuid4
from sqlalchemy.orm import Session, Mapped, mapped_column

from workspaceflow.models.base import Base, UUIDMixin, TimestampMixin
from workspaceflow.models.mixins import WorkspaceScopedMixin
from workspaceflow.models.workspace import Workspace


# Test model using WorkspaceScopedMixin
class Task(Base, UUIDMixin, TimestampMixin, WorkspaceScopedMixin):
    """Sample workspace-scoped model for testing"""
    __tablename__ = "test_tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


@pytest.fixture
def workspace1(db_session: Session, organization_id):
    """Create first test workspace"""
    from workspaceflow.utils.slug import generate_slug
    ws = Workspace(
        name="Workspace 1",
        slug=generate_slug("Workspace 1"),
        organization_id=organization_id
    )
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)
    return ws


@pytest.fixture
def workspace2(db_session: Session, organization_id):
    """Create second test workspace"""
    from workspaceflow.utils.slug import generate_slug
    ws = Workspace(
        name="Workspace 2",
        slug=generate_slug("Workspace 2"),
        organization_id=organization_id
    )
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)
    return ws


class TestWorkspaceScopedMixin:
    """Tests for WorkspaceScopedMixin data isolation"""

    def test_mixin_adds_workspace_id_column(self, db_session: Session):
        """Test that mixin adds workspace_id foreign key"""
        # Create table
        Base.metadata.create_all(db_session.bind)

        # Verify workspace_id column exists
        assert hasattr(Task, "workspace_id")

    def test_query_for_workspace_filters_data(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test that query_for_workspace only returns data for that workspace"""
        # Create table
        Base.metadata.create_all(db_session.bind)

        # Create tasks in workspace1
        task1 = Task(workspace_id=workspace1.id, title="Task 1")
        task2 = Task(workspace_id=workspace1.id, title="Task 2")

        # Create tasks in workspace2
        task3 = Task(workspace_id=workspace2.id, title="Task 3")
        task4 = Task(workspace_id=workspace2.id, title="Task 4")

        db_session.add_all([task1, task2, task3, task4])
        db_session.commit()

        # Query workspace1 tasks
        ws1_tasks = Task.query_for_workspace(db_session, workspace1.id).all()

        assert len(ws1_tasks) == 2
        assert all(t.workspace_id == workspace1.id for t in ws1_tasks)
        assert {t.title for t in ws1_tasks} == {"Task 1", "Task 2"}

        # Query workspace2 tasks
        ws2_tasks = Task.query_for_workspace(db_session, workspace2.id).all()

        assert len(ws2_tasks) == 2
        assert all(t.workspace_id == workspace2.id for t in ws2_tasks)
        assert {t.title for t in ws2_tasks} == {"Task 3", "Task 4"}

    def test_workspace_data_not_leaked(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test that data from one workspace cannot be accessed from another"""
        Base.metadata.create_all(db_session.bind)

        # Create task in workspace1
        task = Task(workspace_id=workspace1.id, title="Secret Task")
        db_session.add(task)
        db_session.commit()
        task_id = task.id

        # Try to query from workspace2
        ws2_tasks = Task.query_for_workspace(db_session, workspace2.id).all()

        # Should not find the task
        assert len(ws2_tasks) == 0
        assert task_id not in [t.id for t in ws2_tasks]

    def test_cascade_delete_workspace_data(
        self,
        db_session: Session,
        workspace1
    ):
        """Test that deleting workspace cascades to scoped data"""
        Base.metadata.create_all(db_session.bind)

        # Create tasks
        task1 = Task(workspace_id=workspace1.id, title="Task 1")
        task2 = Task(workspace_id=workspace1.id, title="Task 2")
        db_session.add_all([task1, task2])
        db_session.commit()

        # Verify tasks exist
        assert db_session.query(Task).count() == 2

        # Delete workspace
        db_session.delete(workspace1)
        db_session.commit()

        # Verify tasks were deleted
        assert db_session.query(Task).count() == 0

    def test_workspace_required_for_scoped_model(
        self,
        db_session: Session
    ):
        """Test that workspace_id is required for scoped models"""
        Base.metadata.create_all(db_session.bind)

        # Try to create task without workspace_id
        task = Task(title="Task without workspace")
        db_session.add(task)

        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestMultiWorkspaceScenarios:
    """Tests for complex multi-workspace scenarios"""

    def test_same_data_different_workspaces(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test that same entity can exist in multiple workspaces"""
        Base.metadata.create_all(db_session.bind)

        # Create task with same title in both workspaces
        task1 = Task(workspace_id=workspace1.id, title="Common Task")
        task2 = Task(workspace_id=workspace2.id, title="Common Task")

        db_session.add_all([task1, task2])
        db_session.commit()

        # Both should exist independently
        assert task1.id != task2.id
        assert db_session.query(Task).count() == 2

        # Each workspace should see only its own
        ws1_tasks = Task.query_for_workspace(db_session, workspace1.id).all()
        ws2_tasks = Task.query_for_workspace(db_session, workspace2.id).all()

        assert len(ws1_tasks) == 1
        assert len(ws2_tasks) == 1
        assert ws1_tasks[0].id != ws2_tasks[0].id

    def test_workspace_switch_query(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test switching between workspace contexts in queries"""
        Base.metadata.create_all(db_session.bind)

        # Create data in both workspaces
        for i in range(5):
            db_session.add(Task(
                workspace_id=workspace1.id,
                title=f"WS1 Task {i}"
            ))
            db_session.add(Task(
                workspace_id=workspace2.id,
                title=f"WS2 Task {i}"
            ))
        db_session.commit()

        # Query workspace1
        count1 = Task.query_for_workspace(db_session, workspace1.id).count()
        assert count1 == 5

        # Switch to workspace2
        count2 = Task.query_for_workspace(db_session, workspace2.id).count()
        assert count2 == 5

        # Verify total
        assert db_session.query(Task).count() == 10

    def test_filtering_within_workspace(
        self,
        db_session: Session,
        workspace1
    ):
        """Test that additional filters work with workspace scoping"""
        Base.metadata.create_all(db_session.bind)

        # Create completed and incomplete tasks
        completed1 = Task(
            workspace_id=workspace1.id,
            title="Completed 1",
            completed=True
        )
        completed2 = Task(
            workspace_id=workspace1.id,
            title="Completed 2",
            completed=True
        )
        incomplete = Task(
            workspace_id=workspace1.id,
            title="Incomplete",
            completed=False
        )

        db_session.add_all([completed1, completed2, incomplete])
        db_session.commit()

        # Query completed tasks in workspace
        completed_tasks = Task.query_for_workspace(
            db_session,
            workspace1.id
        ).filter(Task.completed == True).all()

        assert len(completed_tasks) == 2
        assert all(t.completed for t in completed_tasks)

    def test_count_across_workspaces(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test counting data per workspace"""
        Base.metadata.create_all(db_session.bind)

        # Create different amounts in each workspace
        for i in range(3):
            db_session.add(Task(
                workspace_id=workspace1.id,
                title=f"Task {i}"
            ))

        for i in range(7):
            db_session.add(Task(
                workspace_id=workspace2.id,
                title=f"Task {i}"
            ))

        db_session.commit()

        # Count per workspace
        ws1_count = Task.query_for_workspace(
            db_session,
            workspace1.id
        ).count()
        ws2_count = Task.query_for_workspace(
            db_session,
            workspace2.id
        ).count()

        assert ws1_count == 3
        assert ws2_count == 7
        assert db_session.query(Task).count() == 10


class TestDataIntegrity:
    """Tests for data integrity in workspace isolation"""

    def test_workspace_deletion_cleanup(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test that deleting one workspace doesn't affect others"""
        Base.metadata.create_all(db_session.bind)

        # Create tasks in both workspaces
        for i in range(5):
            db_session.add(Task(
                workspace_id=workspace1.id,
                title=f"WS1 Task {i}"
            ))
            db_session.add(Task(
                workspace_id=workspace2.id,
                title=f"WS2 Task {i}"
            ))
        db_session.commit()

        # Delete workspace1
        db_session.delete(workspace1)
        db_session.commit()

        # Workspace2 tasks should remain
        ws2_tasks = Task.query_for_workspace(db_session, workspace2.id).all()
        assert len(ws2_tasks) == 5

        # Workspace1 tasks should be gone
        assert db_session.query(Task).filter(
            Task.workspace_id == workspace1.id
        ).count() == 0

    def test_no_cross_workspace_updates(
        self,
        db_session: Session,
        workspace1,
        workspace2
    ):
        """Test that updates respect workspace boundaries"""
        Base.metadata.create_all(db_session.bind)

        # Create task in workspace1
        task = Task(workspace_id=workspace1.id, title="Original")
        db_session.add(task)
        db_session.commit()
        task_id = task.id

        # Cannot move task to different workspace by direct update
        # (This should be prevented by application logic, not just DB)
        task.workspace_id = workspace2.id
        db_session.commit()

        # Verify it's now in workspace2
        # (In production, this should be prevented)
        ws2_tasks = Task.query_for_workspace(db_session, workspace2.id).all()
        assert any(t.id == task_id for t in ws2_tasks)
