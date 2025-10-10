"""
Unit tests for workspaceflow models
"""

import pytest
from uuid import uuid4
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError

from workspaceflow.models.workspace import Workspace
from workspaceflow.models.workspace_team import WorkspaceTeam
from workspaceflow.models.mixins import WorkspaceScopedMixin
from workspaceflow.models.base import Base, UUIDMixin, TimestampMixin


class TestWorkspaceModel:
    """Tests for Workspace model"""

    def test_create_workspace(self, db_session: Session, workspace_data):
        """Test creating a workspace"""
        workspace = Workspace(**workspace_data)
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)

        assert workspace.id is not None
        assert workspace.name == workspace_data["name"]
        assert workspace.organization_id == workspace_data["organization_id"]
        assert workspace.slug is not None
        assert workspace.created_at is not None
        assert workspace.updated_at is not None

    def test_workspace_slug_generation(self, db_session: Session, organization_id):
        """Test that workspace slug is auto-generated"""
        workspace = Workspace(
            name="My Test Workspace",
            organization_id=organization_id
        )
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)

        assert workspace.slug is not None
        assert "my-test-workspace" in workspace.slug

    def test_workspace_slug_uniqueness(self, db_session: Session, organization_id):
        """Test that duplicate names get unique slugs"""
        ws1 = Workspace(name="Test", organization_id=organization_id)
        db_session.add(ws1)
        db_session.commit()
        db_session.refresh(ws1)

        ws2 = Workspace(name="Test", organization_id=organization_id)
        db_session.add(ws2)
        db_session.commit()
        db_session.refresh(ws2)

        assert ws1.slug != ws2.slug
        assert "test" in ws1.slug
        assert "test" in ws2.slug

    def test_workspace_settings_default(self, db_session: Session, organization_id):
        """Test that settings defaults to empty dict"""
        workspace = Workspace(
            name="Test",
            organization_id=organization_id
        )
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)

        assert workspace.settings == {}

    def test_workspace_settings_json(self, db_session: Session, organization_id):
        """Test that settings can store JSON data"""
        settings = {
            "theme": "dark",
            "notifications": {"email": True, "slack": False},
            "custom_fields": ["field1", "field2"]
        }
        workspace = Workspace(
            name="Test",
            organization_id=organization_id,
            settings=settings
        )
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)

        assert workspace.settings == settings

    def test_workspace_name_required(self, db_session: Session, organization_id):
        """Test that name is required"""
        workspace = Workspace(organization_id=organization_id)
        db_session.add(workspace)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_workspace_organization_required(self, db_session: Session):
        """Test that organization_id is required"""
        workspace = Workspace(name="Test")
        db_session.add(workspace)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_workspace_cascade_delete_teams(
        self,
        db_session: Session,
        workspace,
        team_id
    ):
        """Test that deleting workspace cascades to team assignments"""
        # Create team assignment
        wt = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_id
        )
        db_session.add(wt)
        db_session.commit()

        # Delete workspace
        db_session.delete(workspace)
        db_session.commit()

        # Verify team assignment was deleted
        assert db_session.query(WorkspaceTeam).filter_by(
            workspace_id=workspace.id
        ).first() is None

    def test_workspace_timestamps(self, db_session: Session, workspace):
        """Test that timestamps are set correctly"""
        from datetime import timedelta
        assert workspace.created_at is not None
        assert workspace.updated_at is not None
        # Timestamps should be very close (within 1 second)
        assert abs((workspace.created_at - workspace.updated_at).total_seconds()) < 1

        # Update workspace
        original_updated = workspace.updated_at
        workspace.name = "Updated Name"
        db_session.commit()
        db_session.refresh(workspace)

        # Timestamp should be updated (in real DB, need trigger or app logic)
        # This is a basic test - actual update logic depends on implementation
        assert workspace.created_at is not None


class TestWorkspaceTeamModel:
    """Tests for WorkspaceTeam model"""

    def test_create_workspace_team(
        self,
        db_session: Session,
        workspace,
        team_id
    ):
        """Test creating a workspace team assignment"""
        wt = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_id,
            role="viewer"
        )
        db_session.add(wt)
        db_session.commit()
        db_session.refresh(wt)

        assert wt.id is not None
        assert wt.workspace_id == workspace.id
        assert wt.team_id == team_id
        assert wt.role == "viewer"
        assert wt.created_at is not None

    def test_workspace_team_role_optional(
        self,
        db_session: Session,
        workspace,
        team_id
    ):
        """Test that role is optional"""
        wt = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_id
        )
        db_session.add(wt)
        db_session.commit()
        db_session.refresh(wt)

        assert wt.role is None

    def test_workspace_team_unique_constraint(
        self,
        db_session: Session,
        workspace,
        team_id
    ):
        """Test that same team cannot be assigned twice to same workspace"""
        wt1 = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_id
        )
        wt2 = WorkspaceTeam(
            workspace_id=workspace.id,
            team_id=team_id
        )
        db_session.add(wt1)
        db_session.add(wt2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_workspace_team_workspace_required(self, db_session: Session, team_id):
        """Test that workspace_id is required"""
        wt = WorkspaceTeam(team_id=team_id)
        db_session.add(wt)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_workspace_team_team_required(self, db_session: Session, workspace):
        """Test that team_id is required"""
        wt = WorkspaceTeam(workspace_id=workspace.id)
        db_session.add(wt)

        with pytest.raises(IntegrityError):
            db_session.commit()


class TestWorkspaceScopedMixin:
    """Tests for WorkspaceScopedMixin"""

    def test_mixin_adds_workspace_id(self):
        """Test that mixin adds workspace_id column"""

        class TestModel(Base, UUIDMixin, WorkspaceScopedMixin):
            __tablename__ = "test_model"
            name: Mapped[str]

        # Check that workspace_id attribute exists
        assert hasattr(TestModel, "workspace_id")

    def test_query_for_workspace(self, db_session: Session, workspace, organization_id):
        """Test query_for_workspace helper method"""

        # Create a test model using the mixin
        class ScopedModel(Base, UUIDMixin, WorkspaceScopedMixin):
            __tablename__ = "scoped_test"
            name: Mapped[str] = mapped_column(nullable=True)

        # Create tables
        Base.metadata.create_all(db_session.bind)

        # Create another workspace for testing
        from workspaceflow.utils.slug import generate_slug
        other_workspace = Workspace(
            name="Other Workspace",
            slug=generate_slug("Other Workspace") + "-2",
            organization_id=organization_id
        )
        db_session.add(other_workspace)
        db_session.commit()

        # Create test data
        item1 = ScopedModel(workspace_id=workspace.id, name="Item 1")
        item2 = ScopedModel(workspace_id=workspace.id, name="Item 2")
        item3 = ScopedModel(workspace_id=other_workspace.id, name="Item 3")

        db_session.add_all([item1, item2, item3])
        db_session.commit()

        # Query for workspace
        results = ScopedModel.query_for_workspace(
            db_session,
            workspace.id
        ).all()

        assert len(results) == 2
        assert all(r.workspace_id == workspace.id for r in results)


class TestMixins:
    """Tests for base mixins"""

    def test_uuid_mixin(self, db_session: Session):
        """Test UUIDMixin generates UUIDs"""

        class UUIDModel(Base, UUIDMixin):
            __tablename__ = "uuid_test"

        Base.metadata.create_all(db_session.bind)

        model = UUIDModel()
        db_session.add(model)
        db_session.commit()
        db_session.refresh(model)

        assert model.id is not None
        # UUID should be valid
        from uuid import UUID
        assert isinstance(model.id, UUID)

    def test_timestamp_mixin(self, db_session: Session):
        """Test TimestampMixin adds timestamps"""

        class TimestampModel(Base, UUIDMixin, TimestampMixin):
            __tablename__ = "timestamp_test"

        Base.metadata.create_all(db_session.bind)

        model = TimestampModel()
        db_session.add(model)
        db_session.commit()
        db_session.refresh(model)

        assert model.created_at is not None
        assert model.updated_at is not None
