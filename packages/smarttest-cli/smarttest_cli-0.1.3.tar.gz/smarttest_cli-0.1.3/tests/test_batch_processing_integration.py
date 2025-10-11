import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.model import Base, ScenarioDB, EndpointDB, SystemDB, Customer, Validation
from service.BatchProcessingService import BatchProcessingService


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_customer(db_session):
    customer = Customer(id="test_customer_id", email="test@example.com")
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_system_and_scenarios(db_session):
    system = SystemDB(id=1, name="Test API", base_url="api.example.com")
    db_session.add(system)
    
    endpoint_get = EndpointDB(id=1, endpoint="/users/123", method="GET", raw_definition={}, system_id=1)
    endpoint_post = EndpointDB(id=2, endpoint="/users", method="POST", raw_definition={}, system_id=1)
    db_session.add(endpoint_get)
    db_session.add(endpoint_post)

    scenarios = [
        ScenarioDB(id=1, name="Get User Success", endpoint_id=endpoint_get.id, requires_auth=False),
        ScenarioDB(id=2, name="Get User Not Found", endpoint_id=endpoint_get.id, requires_auth=False),
        ScenarioDB(id=3, name="Get User Unauthorized", endpoint_id=endpoint_get.id, requires_auth=False),
        ScenarioDB(id=4, name="Create User Success", endpoint_id=endpoint_post.id, requires_auth=False),
    ]
    for s in scenarios:
        db_session.add(s)
    db_session.commit()
    return system, [endpoint_get, endpoint_post], scenarios


class TestBatchProcessingIntegration:
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.httpx.AsyncClient')
    async def test_empty_list_yields_failed_status(self, mock_httpx, db_session, sample_customer):
        service = BatchProcessingService(db_session, sample_customer.id)
        events = []
        async for e in service.process_scenarios_batch([]):
            events.append(e)
        failed_status = [e for e in events if e.event_type == "status" and getattr(e.data, "status", None) == "failed"]
        assert len(failed_status) == 1
    
    @pytest.mark.asyncio
    @patch('service.BatchProcessingService.httpx.AsyncClient')
    async def test_http_error_marks_failed(self, mock_httpx, db_session, sample_customer, sample_system_and_scenarios):
        _, _, scenarios = sample_system_and_scenarios
        client = AsyncMock()
        mock_httpx.return_value.__aenter__.return_value = client
        async def mock_request(*args, **kwargs):
            raise Exception("Network error")
        client.request = mock_request

        service = BatchProcessingService(db_session, sample_customer.id)
        events = []
        async for e in service.process_scenarios_batch([scenarios[0].id]):
            events.append(e)
        scenario_events = [e for e in events if e.event_type == "scenario_result"]
        assert len(scenario_events) == 1
        assert getattr(scenario_events[0].data, "status", None) in ("failed", "error")


