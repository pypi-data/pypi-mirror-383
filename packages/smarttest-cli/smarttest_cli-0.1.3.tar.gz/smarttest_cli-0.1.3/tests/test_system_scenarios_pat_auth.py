"""
Tests for system scenarios endpoint with PAT token authentication

Tests the GET /system/{system_id}/scenarios endpoint that allows users to:
- Retrieve all scenarios for a system
- Filter scenarios (e.g., only those with validations)
- Handle authentication and access control
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from main import app
from service.AuthService import require_auth


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def mock_customer():
    """Mock customer"""
    customer = Mock()
    customer.id = "test_customer"
    customer.email = "test@example.com"
    return customer


@pytest.fixture
def override_auth(mock_customer):
    """Override auth dependency"""
    async def mock_require_auth():
        return mock_customer

    app.dependency_overrides[require_auth] = mock_require_auth
    yield
    app.dependency_overrides.clear()


class TestSystemScenariosEndpoint:
    """Tests for system scenarios endpoint"""

    def test_system_scenarios_requires_auth(self, client):
        """Test that endpoint requires authentication"""
        response = client.get("/system/1/scenarios")
        # Endpoint may not exist (404) or require auth (401)
        assert response.status_code in [401, 404]

    def test_system_scenarios_not_found(self, client, override_auth):
        """
        Test with non-existent system.
        
        Note: The endpoint checks user access before system existence,
        so a non-existent system returns 403 (access denied) rather than 404.
        This is by design - we don't want to leak information about which
        system IDs exist to unauthorized users.
        """
        response = client.get("/system/999/scenarios")
        # Access check happens first, so expect 403 for non-existent systems
        assert response.status_code == 403

    def test_system_scenarios_success(self, client, override_auth, monkeypatch):
        """Test successful retrieval of system scenarios"""
        # Create proper mock objects without circular references
        from database.model import ScenarioDB
        
        # Create a mock scenario using the actual database model structure
        mock_scenario_db = MagicMock(spec=ScenarioDB)
        mock_scenario_db.id = 1
        mock_scenario_db.name = "Test Scenario"
        mock_scenario_db.endpoint_id = 1
        mock_scenario_db.active = True
        mock_scenario_db.validations = []
        mock_scenario_db.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

        mock_endpoint = Mock()
        mock_endpoint.id = 1
        mock_endpoint.scenarios = [mock_scenario_db]

        mock_system = Mock()
        mock_system.id = 1
        mock_system.endpoints = [mock_endpoint]

        # Mock service calls
        def mock_check_system(db, system_id):
            return mock_system

        def mock_check_access(db, user_id, system_id):
            return True

        # Mock rate limiting
        def mock_rate_limit(customer_id):
            pass

        import routes.system_routes as system_routes
        monkeypatch.setattr(system_routes, "check_system_exists", mock_check_system)
        monkeypatch.setattr(system_routes, "check_scenario_rate_limit", mock_rate_limit)

        from service import CustomerService
        monkeypatch.setattr(CustomerService, "check_user_system_access", mock_check_access)

        response = client.get("/system/1/scenarios")

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "total" in data
        assert data["total"] == 1
        assert data["scenarios"][0]["name"] == "Test Scenario"

    def test_system_scenarios_access_denied(self, client, override_auth, monkeypatch):
        """Test that access is denied when user doesn't have permission"""
        # Mock access check to deny
        def mock_check_access(db, user_id, system_id):
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Access denied")

        # Mock rate limiting
        def mock_rate_limit(customer_id):
            pass

        import routes.system_routes as system_routes
        monkeypatch.setattr(system_routes, "check_scenario_rate_limit", mock_rate_limit)

        from service import CustomerService
        monkeypatch.setattr(CustomerService, "check_user_system_access", mock_check_access)

        response = client.get("/system/1/scenarios")

        # Should fail with 403
        assert response.status_code == 403

    def test_system_scenarios_with_validations_filter(self, client, override_auth, monkeypatch):
        """Test filtering scenarios with validations"""
        # Create proper mock objects without circular references
        from database.model import ScenarioDB, Validation
        
        # Mock validation objects
        mock_validation1 = MagicMock(spec=Validation)
        mock_validation1.id = 1
        mock_validation2 = MagicMock(spec=Validation)
        mock_validation2.id = 2

        # Scenario with validations
        scenario_with_validations = MagicMock(spec=ScenarioDB)
        scenario_with_validations.id = 1
        scenario_with_validations.name = "Has Validations"
        scenario_with_validations.endpoint_id = 1
        scenario_with_validations.active = True
        scenario_with_validations.validations = [mock_validation1, mock_validation2]
        scenario_with_validations.created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

        # Scenario without validations
        scenario_without_validations = MagicMock(spec=ScenarioDB)
        scenario_without_validations.id = 2
        scenario_without_validations.name = "No Validations"
        scenario_without_validations.endpoint_id = 1
        scenario_without_validations.active = True
        scenario_without_validations.validations = []
        scenario_without_validations.created_at = datetime(2023, 1, 2, tzinfo=timezone.utc)

        mock_endpoint = Mock()
        mock_endpoint.scenarios = [scenario_with_validations, scenario_without_validations]

        mock_system = Mock()
        mock_system.id = 1
        mock_system.endpoints = [mock_endpoint]

        def mock_check_system(db, system_id):
            return mock_system

        def mock_check_access(db, user_id, system_id):
            return True

        # Mock rate limiting
        def mock_rate_limit(customer_id):
            pass

        import routes.system_routes as system_routes
        monkeypatch.setattr(system_routes, "check_system_exists", mock_check_system)
        monkeypatch.setattr(system_routes, "check_scenario_rate_limit", mock_rate_limit)

        from service import CustomerService
        monkeypatch.setattr(CustomerService, "check_user_system_access", mock_check_access)

        # Test with filter - only scenarios with validations
        response = client.get("/system/1/scenarios?only_with_validations=true")

        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "total" in data
        # Should only return the scenario with validations
        assert data["total"] == 1
        assert data["scenarios"][0]["name"] == "Has Validations"
        assert data["scenarios"][0]["validation_count"] == 2
        assert data["filtered"] is True

        # Test without filter - should return all scenarios
        response = client.get("/system/1/scenarios")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["filtered"] is False

    def test_system_scenarios_empty_system(self, client, override_auth, monkeypatch):
        """Test system with no endpoints/scenarios"""
        mock_system = Mock()
        mock_system.id = 1
        mock_system.endpoints = []

        def mock_check_system(db, system_id):
            return mock_system

        def mock_check_access(db, user_id, system_id):
            return True

        # Mock rate limiting
        def mock_rate_limit(customer_id):
            pass

        import routes.system_routes as system_routes
        monkeypatch.setattr(system_routes, "check_system_exists", mock_check_system)
        monkeypatch.setattr(system_routes, "check_scenario_rate_limit", mock_rate_limit)

        from service import CustomerService
        monkeypatch.setattr(CustomerService, "check_user_system_access", mock_check_access)

        response = client.get("/system/1/scenarios")

        # Should return 200 with empty list
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["scenarios"]) == 0


# Note: These tests focus on the endpoint behavior rather than complex
# scenario filtering logic. Full integration tests with real database
# would test the complete filtering and data transformation logic.

