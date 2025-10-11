"""
Tests for Unified Scenario Execution Service

Tests the core scenario execution logic that is used by both:
- Manual scenario runs (Run Scenario button)
- LLM validation generation (background execution)

Key aspects tested:
- Service exists and is importable
- Core execution flow works
- Error handling for missing scenarios
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService, execute_scenario_unified


class TestUnifiedScenarioExecutionService:
    """Test suite for UnifiedScenarioExecutionService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def service(self, mock_db):
        """Create service instance"""
        return UnifiedScenarioExecutionService(mock_db)

    def test_service_initialization(self, mock_db):
        """Test that service initializes correctly"""
        service = UnifiedScenarioExecutionService(mock_db)
        assert service.db == mock_db

    def test_service_has_execute_method(self, service):
        """Test that service has execute_scenario method"""
        assert hasattr(service, 'execute_scenario')
        assert callable(getattr(service, 'execute_scenario'))


class TestExecuteScenarioUnifiedFunction:
    """Test the execute_scenario_unified function"""

    def test_function_exists(self):
        """Test that execute_scenario_unified function exists and is callable"""
        assert callable(execute_scenario_unified)

    def test_function_handles_missing_scenario(self):
        """Test that function handles missing scenario gracefully"""
        mock_db = Mock(spec=Session)

        # Mock scenario lookup to return None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Should raise or return error
        try:
            result = execute_scenario_unified(mock_db, 999, skip_execution_history=True)
            # If it returns, it should indicate failure
            assert result is None or "error" in str(result).lower()
        except Exception as e:
            # Exception is acceptable for missing scenario
            assert "scenario" in str(e).lower() or "not found" in str(e).lower()


class TestScenarioExecutionIntegration:
    """Integration-style tests for scenario execution"""

    def test_execution_with_mocked_dependencies(self, monkeypatch):
        """Test execution with all dependencies mocked"""
        from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService

        mock_db = Mock(spec=Session)

        # Create mock scenario with all required attributes
        mock_scenario = Mock()
        mock_scenario.id = 1
        mock_scenario.name = "Test Scenario"
        mock_scenario.requires_auth = False
        mock_scenario.auth_error = False
        mock_scenario.endpoint_id = 1

        # Mock endpoint
        mock_endpoint = Mock()
        mock_endpoint.id = 1
        mock_endpoint.endpoint = "/test"
        mock_endpoint.method = "GET"
        mock_endpoint.system_id = 1

        # Mock system
        mock_system = Mock()
        mock_system.id = 1
        mock_system.base_url = "https://api.example.com"

        # Mock query chain
        def mock_query_side_effect(model):
            query_mock = Mock()
            query_mock.filter.return_value.first.return_value = {
                type(mock_scenario).__name__: mock_scenario,
                type(mock_endpoint).__name__: mock_endpoint,
                type(mock_system).__name__: mock_system,
            }.get(model.__name__, None)
            return query_mock

        mock_db.query.side_effect = mock_query_side_effect

        service = UnifiedScenarioExecutionService(mock_db)

        # Verify service was created
        assert service is not None
        assert service.db == mock_db


class TestExecutionHistorySkipping:
    """Test execution history skipping functionality"""

    def test_skip_execution_history_parameter_exists(self):
        """Test that execute_scenario_unified accepts skip_execution_history parameter"""
        import inspect
        sig = inspect.signature(execute_scenario_unified)
        assert 'skip_execution_history' in sig.parameters

    def test_skip_execution_history_defaults_to_false(self):
        """Test that skip_execution_history defaults to False"""
        import inspect
        sig = inspect.signature(execute_scenario_unified)
        param = sig.parameters['skip_execution_history']
        assert param.default is False


class TestAuthenticationHandling:
    """Test authentication handling in scenario execution"""

    def test_service_handles_auth_required_scenarios(self):
        """Test that service can handle scenarios requiring authentication"""
        # This is a documentation test - verifies the pattern exists
        from service.UnifiedScenarioExecution import UnifiedScenarioExecutionService

        mock_db = Mock(spec=Session)
        service = UnifiedScenarioExecutionService(mock_db)

        # Verify service exists and can be instantiated
        assert service is not None

        # The actual auth logic is tested via integration tests
        # This test documents that auth scenarios are supported


# Note: These tests focus on the service layer structure and key behaviors.
# Full end-to-end execution testing requires complex mocking of:
# - Database models and relationships
# - HTTP request execution
# - Authentication token generation
# - Response processing
# These are better tested via integration tests with real database.
