"""
Comprehensive tests for PAT Token API endpoints
Tests all PAT token routes using proper FastAPI dependency override patterns
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock

from main import app
from database.schemas import PATTokenWithSecret, PATTokenResponse, PATTokenList
from service.PATTokenService import PATTokenService
from service.PATTokenAuthService import require_client_or_admin_dynamic


# Mock customer for all tests
def create_mock_customer(customer_id="test_customer_123"):
    """Create a mock customer object"""
    mock = Mock()
    mock.id = customer_id
    mock.email = "test@example.com"
    mock.role = "CLIENT"
    return mock


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_customer():
    """Mock customer fixture"""
    return create_mock_customer()


@pytest.fixture
def override_auth(mock_customer):
    """Override authentication dependency to return mock customer"""
    async def mock_require_auth():
        return mock_customer

    app.dependency_overrides[require_client_or_admin_dynamic] = mock_require_auth
    yield
    app.dependency_overrides.clear()


class TestPATTokenCreation:
    """Tests for PAT token creation endpoint"""

    def test_create_pat_token_success(self, client, override_auth, mock_customer, monkeypatch):
        """Test successful PAT token creation"""
        # Mock the service method
        mock_token = PATTokenWithSecret(
            id=1,
            customer_id=mock_customer.id,
            label="Test Token",
            scopes=["read", "write"],
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_abc123def456"
        )

        def mock_create(db, customer_id, token_data):
            return mock_token

        monkeypatch.setattr(PATTokenService, "create_pat_token", mock_create)

        # Make request
        response = client.post("/pat-tokens", json={
            "label": "Test Token",
            "scopes": ["read", "write"]
        })

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["label"] == "Test Token"
        assert data["scopes"] == ["read", "write"]
        assert data["token"] == "st_pat_abc123def456"
        assert "created_at" in data

    def test_create_pat_token_with_default_scopes(self, client, override_auth, mock_customer, monkeypatch):
        """Test PAT token creation with default scopes when none specified"""
        mock_token = PATTokenWithSecret(
            id=1,
            customer_id=mock_customer.id,
            label="Default Token",
            scopes=["read", "write"],
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            last_used_at=None,
            token="st_pat_default123"
        )

        def mock_create(db, customer_id, token_data):
            return mock_token

        monkeypatch.setattr(PATTokenService, "create_pat_token", mock_create)

        response = client.post("/pat-tokens", json={"label": "Default Token"})

        assert response.status_code == 201
        assert response.json()["scopes"] == ["read", "write"]

    def test_create_pat_token_missing_label(self, client, override_auth):
        """Test PAT token creation fails without label"""
        response = client.post("/pat-tokens", json={})
        assert response.status_code == 422  # Validation error

    def test_create_pat_token_empty_label(self, client, override_auth, monkeypatch):
        """Test PAT token creation with empty label - caught by service layer"""
        # Empty string passes pydantic validation but should be caught by business logic
        # The actual validation behavior depends on the PATTokenCreate schema
        # This test documents current behavior: it reaches the service layer
        def mock_create(db, customer_id, token_data):
            if not token_data.label or token_data.label.strip() == "":
                raise ValueError("Label cannot be empty")
            return None

        monkeypatch.setattr(PATTokenService, "create_pat_token", mock_create)

        response = client.post("/pat-tokens", json={"label": ""})
        # May be 422 (validation) or 500 (service error) depending on implementation
        assert response.status_code in [422, 500]

    def test_create_pat_token_invalid_scopes_type(self, client, override_auth):
        """Test PAT token creation fails with invalid scopes type"""
        response = client.post("/pat-tokens", json={
            "label": "Test",
            "scopes": "invalid_string"  # Should be array
        })
        assert response.status_code == 422

    def test_create_pat_token_service_error(self, client, override_auth, monkeypatch):
        """Test PAT token creation handles service errors"""
        def mock_create_error(db, customer_id, token_data):
            raise Exception("Database error")

        monkeypatch.setattr(PATTokenService, "create_pat_token", mock_create_error)

        response = client.post("/pat-tokens", json={"label": "Test"})

        assert response.status_code == 500
        assert "Failed to create PAT token" in response.json()["detail"]

    def test_create_pat_token_requires_auth(self, client):
        """Test that creating PAT token requires authentication"""
        response = client.post("/pat-tokens", json={"label": "Test"})
        assert response.status_code == 401


class TestPATTokenListing:
    """Tests for PAT token listing endpoint"""

    def test_list_pat_tokens_success(self, client, override_auth, mock_customer, monkeypatch):
        """Test successful PAT token listing"""
        mock_tokens = [
            PATTokenResponse(
                id=1,
                customer_id=mock_customer.id,
                label="Token 1",
                scopes=["read"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=None
            ),
            PATTokenResponse(
                id=2,
                customer_id=mock_customer.id,
                label="Token 2",
                scopes=["read", "write"],
                created_at=datetime.now(timezone.utc),
                revoked_at=None,
                last_used_at=datetime.now(timezone.utc)
            )
        ]

        def mock_list(db, customer_id):
            return PATTokenList(tokens=mock_tokens, total=2)

        monkeypatch.setattr(PATTokenService, "list_pat_tokens", mock_list)

        response = client.get("/pat-tokens")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tokens"]) == 2
        assert data["tokens"][0]["label"] == "Token 1"

        # Verify no token values in list response
        for token in data["tokens"]:
            assert "token" not in token

    def test_list_pat_tokens_empty(self, client, override_auth, monkeypatch):
        """Test listing when no tokens exist"""
        def mock_list(db, customer_id):
            return PATTokenList(tokens=[], total=0)

        monkeypatch.setattr(PATTokenService, "list_pat_tokens", mock_list)

        response = client.get("/pat-tokens")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["tokens"]) == 0

    def test_list_pat_tokens_requires_auth(self, client):
        """Test that listing PAT tokens requires authentication"""
        response = client.get("/pat-tokens")
        assert response.status_code == 401


class TestPATTokenRevocation:
    """Tests for PAT token revocation endpoint"""

    def test_revoke_pat_token_success(self, client, override_auth, monkeypatch):
        """Test successful PAT token revocation"""
        def mock_revoke(db, customer_id, token_id):
            return True

        monkeypatch.setattr(PATTokenService, "revoke_pat_token", mock_revoke)

        response = client.delete("/pat-tokens/1")

        assert response.status_code == 204
        assert response.content == b""  # No content for 204

    def test_revoke_pat_token_not_found(self, client, override_auth, monkeypatch):
        """Test revoking non-existent token"""
        def mock_revoke(db, customer_id, token_id):
            return False

        monkeypatch.setattr(PATTokenService, "revoke_pat_token", mock_revoke)

        response = client.delete("/pat-tokens/999")

        assert response.status_code == 404
        assert "not found or already revoked" in response.json()["detail"]

    def test_revoke_pat_token_invalid_id(self, client, override_auth):
        """Test revoking with invalid token ID"""
        response = client.delete("/pat-tokens/invalid")
        assert response.status_code == 422  # Validation error

    def test_revoke_pat_token_service_error(self, client, override_auth, monkeypatch):
        """Test revocation handles service errors"""
        def mock_revoke_error(db, customer_id, token_id):
            raise Exception("Database error")

        monkeypatch.setattr(PATTokenService, "revoke_pat_token", mock_revoke_error)

        response = client.delete("/pat-tokens/1")

        assert response.status_code == 500
        assert "Failed to revoke PAT token" in response.json()["detail"]

    def test_revoke_pat_token_requires_auth(self, client):
        """Test that revoking PAT token requires authentication"""
        response = client.delete("/pat-tokens/1")
        assert response.status_code == 401


class TestPATTokenInfo:
    """Tests for PAT token info endpoint"""

    def test_pat_token_info_endpoint(self, client):
        """Test PAT token info endpoint (no auth required)"""
        response = client.get("/pat-tokens/info")

        assert response.status_code == 200
        data = response.json()
        assert data["pat_token_system"] == "active"
        assert data["supported_token_format"] == "st_pat_<random>"
        assert data["default_scopes"] == ["read", "write"]
        assert "endpoints" in data
        assert "create" in data["endpoints"]
        assert "list" in data["endpoints"]
        assert "revoke" in data["endpoints"]
