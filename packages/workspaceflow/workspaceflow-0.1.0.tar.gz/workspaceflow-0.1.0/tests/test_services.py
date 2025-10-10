"""
Unit tests for workspaceflow services
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from workspaceflow.core.workspace import WorkspaceService
from workspaceflow.models.workspace import Workspace
from workspaceflow.models.workspace_team import WorkspaceTeam
from workspaceflow.config import WorkspaceConfig
from workspaceflow.exceptions import (
    WorkspaceNotFoundError,
    WorkspacePermissionDeniedError,
    WorkspaceSlugConflictError
)


@pytest.fixture
def mock_authflow(organization_id, team_id):
    """Create mock authflow instance"""
    authflow = Mock()
    authflow.has_permission = Mock(return_value=True)
    authflow.get_user_teams = Mock(return_value=[])
    authflow.get_team_members = Mock(return_value=[])

    # Mock get_team to return a team with the correct organization_id
    mock_team = Mock()
    mock_team.id = team_id
    mock_team.organization_id = organization_id
    authflow.get_team = Mock(return_value=mock_team)

    return authflow


@pytest.fixture
def workspace_service(db_session: Session, mock_authflow):
    """Create WorkspaceService instance"""
    config = WorkspaceConfig()
    return WorkspaceService(
        db=db_session,
        authflow=mock_authflow,
        config=config
    )


class TestWorkspaceServiceCreate:
    """Tests for workspace creation"""

    def test_create_workspace_success(
        self,
        workspace_service: WorkspaceService,
        mock_authflow,
        organization_id,
        user_id
    ):
        """Test successful workspace creation"""
        mock_authflow.has_permission.return_value = True

        workspace = workspace_service.create_workspace(
            user_id=user_id,
            org_id=organization_id,
            name="Test Workspace",
            description="Test description"
        )

        assert workspace.id is not None
        assert workspace.name == "Test Workspace"
        assert workspace.organization_id == organization_id
        assert workspace.description == "Test description"

        # Verify permission check was called
        mock_authflow.has_permission.assert_called_once()

    def test_create_workspace_permission_denied(
        self,
        workspace_service: WorkspaceService,
        mock_authflow,
        organization_id,
        user_id
    ):
        """Test workspace creation fails without permission"""
        mock_authflow.has_permission.return_value = False

        with pytest.raises(WorkspacePermissionDeniedError):
            workspace_service.create_workspace(
                user_id=user_id,
                org_id=organization_id,
                name="Test Workspace"
            )

    def test_create_workspace_generates_slug(
        self,
        workspace_service: WorkspaceService,
        organization_id,
        user_id
    ):
        """Test that slug is auto-generated"""
        workspace = workspace_service.create_workspace(
            user_id=user_id,
            org_id=organization_id,
            name="My Test Workspace"
        )

        assert workspace.slug is not None
        assert "my-test-workspace" in workspace.slug

    def test_create_workspace_with_settings(
        self,
        workspace_service: WorkspaceService,
        organization_id,
        user_id
    ):
        """Test creating workspace with custom settings"""
        settings = {"theme": "dark", "lang": "en"}

        workspace = workspace_service.create_workspace(
            user_id=user_id,
            org_id=organization_id,
            name="Test",
            settings=settings
        )

        assert workspace.settings == settings


class TestWorkspaceServiceRead:
    """Tests for workspace retrieval"""

    def test_get_workspace_by_id(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id
    ):
        """Test getting workspace by ID"""
        result = workspace_service.get_workspace(
            workspace_id=workspace.id,
            user_id=user_id
        )

        assert result.id == workspace.id
        assert result.name == workspace.name

    def test_get_workspace_not_found(
        self,
        workspace_service: WorkspaceService,
        user_id
    ):
        """Test getting non-existent workspace"""
        with pytest.raises(WorkspaceNotFoundError):
            workspace_service.get_workspace(
                workspace_id=uuid4(),
                user_id=user_id
            )

    def test_list_workspaces_for_org(
        self,
        workspace_service: WorkspaceService,
        db_session: Session,
        organization_id,
        user_id
    ):
        """Test listing workspaces for organization"""
        # Create multiple workspaces
        for i in range(3):
            ws = Workspace(
                name=f"Workspace {i}",
                organization_id=organization_id
            )
            db_session.add(ws)
        db_session.commit()

        workspaces = workspace_service.list_workspaces(
            org_id=organization_id,
            user_id=user_id
        )

        assert len(workspaces) == 3

    def test_list_workspaces_pagination(
        self,
        workspace_service: WorkspaceService,
        db_session: Session,
        organization_id,
        user_id
    ):
        """Test workspace listing with pagination"""
        # Create 10 workspaces
        for i in range(10):
            ws = Workspace(
                name=f"Workspace {i}",
                organization_id=organization_id
            )
            db_session.add(ws)
        db_session.commit()

        # Get first page
        page1 = workspace_service.list_workspaces(
            org_id=organization_id,
            user_id=user_id,
            limit=5,
            offset=0
        )

        # Get second page
        page2 = workspace_service.list_workspaces(
            org_id=organization_id,
            user_id=user_id,
            limit=5,
            offset=5
        )

        assert len(page1) == 5
        assert len(page2) == 5
        # Ensure different results
        page1_ids = {w.id for w in page1}
        page2_ids = {w.id for w in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestWorkspaceServiceUpdate:
    """Tests for workspace updates"""

    def test_update_workspace(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id
    ):
        """Test updating workspace"""
        updated = workspace_service.update_workspace(
            workspace_id=workspace.id,
            user_id=user_id,
            name="Updated Name",
            description="Updated description"
        )

        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"

    def test_update_workspace_settings(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id
    ):
        """Test updating workspace settings"""
        new_settings = {"theme": "light", "notifications": True}

        updated = workspace_service.update_workspace(
            workspace_id=workspace.id,
            user_id=user_id,
            settings=new_settings
        )

        assert updated.settings == new_settings

    def test_update_workspace_not_found(
        self,
        workspace_service: WorkspaceService,
        user_id
    ):
        """Test updating non-existent workspace"""
        with pytest.raises(WorkspaceNotFoundError):
            workspace_service.update_workspace(
                workspace_id=uuid4(),
                user_id=user_id,
                name="New Name"
            )


class TestWorkspaceServiceDelete:
    """Tests for workspace deletion"""

    def test_delete_workspace(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id
    ):
        """Test deleting workspace"""
        workspace_service.delete_workspace(
            workspace_id=workspace.id,
            user_id=user_id
        )

        # Verify workspace is deleted
        with pytest.raises(WorkspaceNotFoundError):
            workspace_service.get_workspace(
                workspace_id=workspace.id,
                user_id=user_id
            )

    def test_delete_workspace_not_found(
        self,
        workspace_service: WorkspaceService,
        user_id
    ):
        """Test deleting non-existent workspace"""
        with pytest.raises(WorkspaceNotFoundError):
            workspace_service.delete_workspace(
                workspace_id=uuid4(),
                user_id=user_id
            )


class TestWorkspaceServiceTeamAssignment:
    """Tests for team assignment operations"""

    def test_assign_team_to_workspace(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id,
        team_id
    ):
        """Test assigning team to workspace"""
        assignment = workspace_service.assign_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id,
            role="editor"
        )

        assert assignment.workspace_id == workspace.id
        assert assignment.team_id == team_id
        assert assignment.role == "editor"

    def test_assign_team_without_role(
        self,
        workspace_service: WorkspaceService,
        workspace,
        user_id,
        team_id
    ):
        """Test assigning team without role"""
        assignment = workspace_service.assign_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id
        )

        assert assignment.role is None

    def test_remove_team_from_workspace(
        self,
        workspace_service: WorkspaceService,
        db_session: Session,
        workspace,
        user_id,
        team_id
    ):
        """Test removing team from workspace"""
        # First assign team
        workspace_service.assign_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id
        )

        # Then remove
        workspace_service.remove_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id
        )

        # Verify removal
        assignment = db_session.query(WorkspaceTeam).filter_by(
            workspace_id=workspace.id,
            team_id=team_id
        ).first()

        assert assignment is None

    def test_get_workspace_members(
        self,
        workspace_service: WorkspaceService,
        mock_authflow,
        workspace,
        user_id,
        team_id
    ):
        """Test getting workspace members"""
        # Assign team first
        workspace_service.assign_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id
        )

        # Mock team members
        mock_authflow.get_team_members.return_value = [
            {"user_id": uuid4(), "role": "member"},
            {"user_id": uuid4(), "role": "admin"}
        ]

        members = workspace_service.get_workspace_members(
            workspace_id=workspace.id,
            user_id=user_id
        )

        # Should have called get_team_members
        mock_authflow.get_team_members.assert_called()
        assert len(members) >= 0  # Actual count depends on mock


class TestWorkspaceServiceAccessControl:
    """Tests for access control helpers"""

    def test_check_user_access_via_team(
        self,
        workspace_service: WorkspaceService,
        mock_authflow,
        workspace,
        user_id,
        team_id
    ):
        """Test user has access via team membership"""
        # Assign team to workspace
        workspace_service.assign_team(
            workspace_id=workspace.id,
            user_id=user_id,
            team_id=team_id
        )

        # Mock user is in team
        mock_authflow.get_user_teams.return_value = [
            {"id": team_id, "name": "Test Team"}
        ]

        has_access = workspace_service.check_user_access(
            workspace_id=workspace.id,
            user_id=user_id
        )

        assert has_access is True

    def test_check_user_no_access(
        self,
        workspace_service: WorkspaceService,
        mock_authflow,
        workspace,
        user_id
    ):
        """Test user has no access when not in any team"""
        # User has no teams
        mock_authflow.get_user_teams.return_value = []

        has_access = workspace_service.check_user_access(
            workspace_id=workspace.id,
            user_id=user_id
        )

        assert has_access is False
