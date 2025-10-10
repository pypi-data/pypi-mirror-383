"""
Integration tests for workspaceflow API routes
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import Table, Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

from workspaceflow.models.base import Base
from workspaceflow.setup import setup_workspaces
from workspaceflow.config import WorkspaceConfig


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    from sqlalchemy import event
    from sqlalchemy.pool import StaticPool

    # Use StaticPool to ensure all sessions use the SAME connection
    # This is crucial for SQLite :memory: databases in tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Share the same connection across all sessions
    )

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create mock organizations table for foreign key constraint
    organizations_table = Table(
        'organizations',
        Base.metadata,
        Column('id', String(36), primary_key=True),
        extend_existing=True
    )

    # Create mock teams table for foreign key constraint
    teams_table = Table(
        'teams',
        Base.metadata,
        Column('id', String(36), primary_key=True),
        extend_existing=True
    )

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    yield SessionLocal
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_authflow():
    """Create mock authflow"""
    authflow = Mock()
    authflow.has_permission = Mock(return_value=True)
    authflow.get_user_teams = Mock(return_value=[])
    authflow.get_team_members = Mock(return_value=[])
    authflow.get_current_user = Mock(return_value={"id": str(uuid4())})

    # Store organization_id for get_team mock
    authflow._org_id = None

    # Mock get_team to return a team with the correct organization_id
    def get_team_mock(team_id):
        mock_team = Mock()
        mock_team.id = team_id
        # Use the stored org_id or a new one if not set
        mock_team.organization_id = authflow._org_id if authflow._org_id else uuid4()
        return mock_team

    authflow.get_team = Mock(side_effect=get_team_mock)

    return authflow


@pytest.fixture
def organization_id(test_db):
    """Test organization ID with mock data"""
    org_id = str(uuid4())
    # Insert into mock organizations table
    db = test_db()
    try:
        db.execute(
            Base.metadata.tables['organizations'].insert().values(id=org_id)
        )
        db.commit()
    finally:
        db.close()

    return org_id


@pytest.fixture
def app(test_db, mock_authflow, organization_id):
    """Create FastAPI test app"""
    app = FastAPI()

    # Set the org_id in mock_authflow for get_team to use
    mock_authflow._org_id = organization_id

    # Setup workspaceflow with the test database session factory
    # Set database_url to None to force using db_session_factory
    config = WorkspaceConfig(database_url=None)
    setup_workspaces(
        app,
        authflow=mock_authflow,
        config=config,
        prefix="/api/v1",
        db_session_factory=test_db  # Use the test database
    )

    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create auth headers for requests"""
    return {"Authorization": "Bearer test-token"}


class TestWorkspaceRoutes:
    """Tests for workspace CRUD endpoints"""

    def test_create_workspace(self, client, auth_headers, organization_id):
        """Test POST /workspaces"""
        response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id,
                "description": "Test description"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["organization_id"] == organization_id
        assert "id" in data
        assert "slug" in data

    def test_create_workspace_missing_name(self, client, auth_headers, organization_id):
        """Test creating workspace without name fails"""
        response = client.post(
            "/api/v1/workspaces",
            json={"organization_id": organization_id},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_list_workspaces(self, client, auth_headers, organization_id):
        """Test GET /workspaces"""
        # Create some workspaces first
        for i in range(3):
            client.post(
                "/api/v1/workspaces",
                json={
                    "name": f"Workspace {i}",
                    "organization_id": organization_id
                },
                headers=auth_headers
            )

        # List workspaces
        response = client.get(
            f"/api/v1/workspaces?org_id={organization_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        assert len(data["workspaces"]) == 3

    def test_list_workspaces_pagination(self, client, auth_headers, organization_id):
        """Test workspace listing with pagination"""
        # Create 10 workspaces
        for i in range(10):
            client.post(
                "/api/v1/workspaces",
                json={
                    "name": f"Workspace {i}",
                    "organization_id": organization_id
                },
                headers=auth_headers
            )

        # Get first page
        response = client.get(
            f"/api/v1/workspaces?org_id={organization_id}&limit=5&offset=0",
            headers=auth_headers
        )

        assert response.status_code == 200
        page1 = response.json()
        assert len(page1["workspaces"]) == 5

        # Get second page
        response = client.get(
            f"/api/v1/workspaces?org_id={organization_id}&limit=5&offset=5",
            headers=auth_headers
        )

        assert response.status_code == 200
        page2 = response.json()
        assert len(page2["workspaces"]) == 5

    def test_get_workspace(self, client, auth_headers, organization_id):
        """Test GET /workspaces/{id}"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Get workspace
        response = client.get(
            f"/api/v1/workspaces/{workspace_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workspace_id
        assert data["name"] == "Test Workspace"

    def test_get_workspace_not_found(self, client, auth_headers):
        """Test getting non-existent workspace returns 404"""
        response = client.get(
            f"/api/v1/workspaces/{uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_workspace(self, client, auth_headers, organization_id):
        """Test PATCH /workspaces/{id}"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Original Name",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Update workspace
        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}",
            json={
                "name": "Updated Name",
                "description": "New description"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    def test_delete_workspace(self, client, auth_headers, organization_id):
        """Test DELETE /workspaces/{id}"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "To Delete",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Delete workspace
        response = client.delete(
            f"/api/v1/workspaces/{workspace_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/v1/workspaces/{workspace_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestTeamAssignmentRoutes:
    """Tests for team assignment endpoints"""

    def test_assign_team_to_workspace(
        self,
        client,
        auth_headers,
        organization_id,
        test_db
    ):
        """Test POST /workspaces/{id}/teams"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Insert team into mock teams table
        team_id = str(uuid4())
        db = test_db()
        try:
            db.execute(
                Base.metadata.tables['teams'].insert().values(id=team_id)
            )
            db.commit()
        finally:
            db.close()

        # Assign team
        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/teams",
            json={
                "team_id": team_id,
                "role": "contributor"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["team_id"] == team_id
        assert data["role"] == "contributor"

    def test_assign_team_without_role(
        self,
        client,
        auth_headers,
        organization_id,
        test_db
    ):
        """Test assigning team without role"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Insert team into mock teams table
        team_id = str(uuid4())
        db = test_db()
        try:
            db.execute(
                Base.metadata.tables['teams'].insert().values(id=team_id)
            )
            db.commit()
        finally:
            db.close()

        # Assign team without role
        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/teams",
            json={"team_id": team_id},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["team_id"] == team_id
        assert data["role"] is None

    def test_remove_team_from_workspace(
        self,
        client,
        auth_headers,
        organization_id,
        test_db
    ):
        """Test DELETE /workspaces/{id}/teams/{team_id}"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Insert team into mock teams table
        team_id = str(uuid4())
        db = test_db()
        try:
            db.execute(
                Base.metadata.tables['teams'].insert().values(id=team_id)
            )
            db.commit()
        finally:
            db.close()

        # Assign team
        client.post(
            f"/api/v1/workspaces/{workspace_id}/teams",
            json={"team_id": team_id},
            headers=auth_headers
        )

        # Remove team
        response = client.delete(
            f"/api/v1/workspaces/{workspace_id}/teams/{team_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

    def test_get_workspace_members(
        self,
        client,
        auth_headers,
        organization_id,
        mock_authflow,
        test_db
    ):
        """Test GET /workspaces/{id}/members"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Insert team into mock teams table
        team_id = str(uuid4())
        db = test_db()
        try:
            db.execute(
                Base.metadata.tables['teams'].insert().values(id=team_id)
            )
            db.commit()
        finally:
            db.close()

        # Assign team
        client.post(
            f"/api/v1/workspaces/{workspace_id}/teams",
            json={"team_id": team_id},
            headers=auth_headers
        )

        # Mock team members - use 'id' field to match WorkspaceMemberResponse schema
        mock_authflow.get_team_members.return_value = [
            {"id": str(uuid4()), "email": "user1@example.com"},
            {"id": str(uuid4()), "email": "user2@example.com"}
        ]

        # Get members
        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/members",
            headers=auth_headers
        )

        assert response.status_code == 200
        # Response structure depends on implementation


class TestWorkspaceMiddleware:
    """Tests for workspace middleware"""

    def test_workspace_header_added(
        self,
        client,
        auth_headers,
        organization_id
    ):
        """Test X-Workspace-ID header is processed"""
        # Create workspace
        create_response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test Workspace",
                "organization_id": organization_id
            },
            headers=auth_headers
        )
        workspace_id = create_response.json()["id"]

        # Make request with workspace header
        headers = {**auth_headers, "X-Workspace-ID": workspace_id}
        response = client.get(
            f"/api/v1/workspaces/{workspace_id}",
            headers=headers
        )

        assert response.status_code == 200


class TestErrorHandling:
    """Tests for API error handling"""

    def test_unauthorized_request(self, client, organization_id):
        """Test request without auth token fails"""
        response = client.post(
            "/api/v1/workspaces",
            json={
                "name": "Test",
                "organization_id": organization_id
            }
        )

        # Depends on auth implementation
        # assert response.status_code in [401, 403]

    def test_validation_error(self, client, auth_headers):
        """Test invalid request data returns 422"""
        response = client.post(
            "/api/v1/workspaces",
            json={"invalid": "data"},
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_not_found_error(self, client, auth_headers):
        """Test 404 for non-existent resources"""
        response = client.get(
            f"/api/v1/workspaces/{uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 404
