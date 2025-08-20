# conftest.py
import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from app.crud.repositories import LiteAuditLogRepo, LiteUserRepo
from app.crud.uow import AsyncUnitOfWork
from app.database import get_db_session

# Import your app components
from app.main import app
from app.models import Base
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ==================== PYTEST CONFIG ====================
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# ==================== EVENT LOOP ====================
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==================== DATABASE FIXTURES ====================
@pytest.fixture(scope="session")
def sync_engine():
    """Synchronous engine untuk setup database."""
    return create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


@pytest.fixture(scope="session")
def async_engine():
    """Async engine untuk testing."""
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Fresh database session untuk setiap test."""
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    # Cleanup - drop tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ==================== REPOSITORY FIXTURES ====================
@pytest.fixture
def user_repository(async_session: AsyncSession) -> LiteUserRepo:
    """LiteUserRepo instance untuk testing."""
    return LiteUserRepo(async_session)


@pytest.fixture
def auditlog_repository(async_session: AsyncSession) -> LiteAuditLogRepo:
    """LiteAuditLogRepo instance untuk testing."""
    return LiteAuditLogRepo(async_session)


# ==================== UOW FIXTURES ====================
@pytest.fixture
def uow(async_session: AsyncSession) -> AsyncUnitOfWork:
    """UnitOfWork instance untuk testing."""
    return AsyncUnitOfWork(async_session)


@pytest.fixture
def uow_factory(async_session: AsyncSession):
    """UoW factory untuk testing."""
    return lambda: AsyncUnitOfWork(async_session)


# # ==================== MOCK FIXTURES ====================
# @pytest.fixture
# def mock_httpx_client():
#     """Mock HTTP client untuk external API calls."""
#     mock_client = AsyncMock()

#     # Mock successful supplier response
#     mock_response = Mock()
#     mock_response.json.return_value = {
#         "success": True,
#         "supplier_order_id": "SUP123",
#         "status": "accepted"
#     }
#     mock_response.raise_for_status = Mock()

#     mock_client.post.return_value = mock_response
#     return mock_client

# @pytest.fixture
# def mock_supplier_api(monkeypatch, mock_httpx_client):
#     """Mock supplier API calls in services."""
#     async def mock_call_supplier_api(self, request_data):
#         return {
#             "success": True,
#             "supplier_order_id": "SUP123",
#             "status": "accepted"
#         }

#     # Patch the method in OrderService
#     monkeypatch.setattr(
#         "app.services.order_service.OrderService._call_supplier_api",
#         mock_call_supplier_api
#     )

# # ==================== SERVICE FIXTURES ====================
# @pytest.fixture
# def order_service(inbox_repository, product_repository, uow_factory) -> OrderService:
#     """OrderService instance untuk testing."""
#     return OrderService(inbox_repository, product_repository, uow_factory)

# @pytest.fixture
# def order_service_with_mocks(
#     inbox_repository,
#     product_repository,
#     uow_factory,
#     mock_supplier_api
# ) -> OrderService:
#     """OrderService dengan mocked external dependencies."""
#     return OrderService(inbox_repository, product_repository, uow_factory)

# ==================== FASTAPI FIXTURES ====================
# @pytest.fixture
# def test_client() -> TestClient:
#     """FastAPI test client."""
#     return TestClient(app)

# @pytest_asyncio.fixture
# async def async_client() -> AsyncGenerator[AsyncClient, None]:
#     """Async HTTP client untuk testing FastAPI endpoints."""
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client


# Override database dependency untuk testing
@pytest.fixture(autouse=True)
def override_get_db(async_session):
    """Override database dependency dengan test session."""

    async def get_test_db():
        yield async_session

    app.dependency_overrides[get_db_session] = get_test_db
    yield
    app.dependency_overrides.clear()


# # ==================== TEST DATA FIXTURES ====================
# @pytest.fixture
# def sample_inbox_data():
#     """Sample data untuk inbox testing."""
#     return {
#         "request_id": "REQ001",
#         "payload": {
#             "product_id": "PROD123",
#             "amount": 100.00,
#             "customer_id": "CUST456"
#         },
#         "status": "received"
#     }

# @pytest.fixture
# def sample_product_data():
#     """Sample data untuk product testing."""
#     return {
#         "code": "PROD123",
#         "name": "Test Product",
#         "price": 100.00,
#         "is_available": True,
#         "stock": 50
#     }

# @pytest.fixture
# def sample_transaction_data():
#     """Sample data untuk transaction testing."""
#     return {
#         "inbox_id": 1,
#         "product_id": "PROD123",
#         "amount": 100.00,
#         "status": "pending"
#     }

# @pytest.fixture
# def sample_order_request():
#     """Sample order request untuk integration testing."""
#     return {
#         "request_id": "REQ001",
#         "product_id": "PROD123",
#         "amount": 100.00,
#         "customer_id": "CUST456",
#         "priority": "normal"
#     }


# ==================== SETUP/TEARDOWN FIXTURES ====================
# @pytest_asyncio.fixture
# async def setup_test_data(async_session: AsyncSession, sample_product_data):
#     """Setup initial test data."""
#     from app.models import Product

#     # Create test product
#     product = Product(**sample_product_data)
#     async_session.add(product)
#     await async_session.commit()
#     await async_session.refresh(product)

#     return {"product": product}


# ==================== CUSTOM ASSERTIONS ====================
class DatabaseAssertions:
    """Custom assertions untuk database testing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # async def assert_inbox_exists(self, request_id: str, expected_status: str = None):
    #     """Assert inbox message exists dengan status tertentu."""
    #     from app.models import InboxMessage
    #     from sqlalchemy import select

    #     result = await self.session.execute(
    #         select(InboxMessage).where(InboxMessage.request_id == request_id)
    #     )
    #     inbox = result.scalar_one_or_none()

    #     assert inbox is not None, (
    #         f"Inbox dengan request_id {request_id} tidak ditemukan"
    #     )

    #     if expected_status:
    #         assert inbox.status == expected_status, (
    #             f"Expected status {expected_status}, got {inbox.status}"
    #         )

    #     return inbox

    # async def assert_transaction_exists(
    #     self, inbox_id: int, expected_status: str = None
    # ):
    #     """Assert transaction exists untuk inbox tertentu."""
    #     from app.models import Transaction
    #     from sqlalchemy import select

    #     result = await self.session.execute(
    #         select(Transaction).where(Transaction.inbox_id == inbox_id)
    #     )
    #     transaction = result.scalar_one_or_none()

    #     assert transaction is not None, (
    #         f"Transaction untuk inbox_id {inbox_id} tidak ditemukan"
    #     )

    #     if expected_status:
    #         assert transaction.status == expected_status, (
    #             f"Expected status {expected_status}, got {transaction.status}"
    #         )

    #     return transaction

    # async def assert_outbox_exists(self, transaction_id: int):
    #     """Assert outbox message exists untuk transaction tertentu."""
    #     from app.models import OutboxMessage
    #     from sqlalchemy import select

    #     result = await self.session.execute(
    #         select(OutboxMessage).where(OutboxMessage.transaction_id == transaction_id)
    #     )
    #     outbox = result.scalar_one_or_none()

    #     assert outbox is not None, (
    #         f"Outbox untuk transaction_id {transaction_id} tidak ditemukan"
    #     )
    #     return outbox

    # async def assert_tables_empty(self):
    #     """Assert semua tables kosong (untuk cleanup testing)."""
    #     from app.models import InboxMessage, OutboxMessage, Transaction
    #     from sqlalchemy import func, select

    #     tables = [InboxMessage, Transaction, OutboxMessage]
    #     for table in tables:
    #         result = await self.session.execute(select(func.count(table.id)))
    #         count = result.scalar()
    #         assert count == 0, f"Table {table.__tablename__} masih ada {count} records"


@pytest.fixture
def db_assertions(async_session: AsyncSession) -> DatabaseAssertions:
    """Database assertions helper."""
    return DatabaseAssertions(async_session)


# ==================== PARAMETRIZED FIXTURES ====================
@pytest.fixture(params=["received", "processing", "completed", "failed"])
def inbox_status(request):
    """Parametrized inbox status untuk testing berbagai scenarios."""
    return request.param


@pytest.fixture(
    params=[
        {"success": True, "supplier_order_id": "SUP123"},
        {"success": False, "error": "Product unavailable"},
    ]
)
def supplier_responses(request):
    """Parametrized supplier responses."""
    return request.param


# ==================== CLEANUP FIXTURES ====================
@pytest.fixture(autouse=True)
async def cleanup_after_test(async_session: AsyncSession):
    """Auto cleanup setelah setiap test."""
    yield  # Test runs here

    # Cleanup - rollback any uncommitted changes
    await async_session.rollback()


# ==================== EXAMPLE USAGE IN TESTS ====================
# """
# # Example test file: test_order_service.py

# import pytest
# from unittest.mock import patch

# class TestOrderServiceSimple:
#     '''Test simple operations - direct repository'''

#     @pytest.mark.asyncio
#     async def test_get_inbox_messages(self, order_service, setup_test_data):
#         # Test simple read operation
#         messages = await order_service.get_inbox_messages()
#         assert isinstance(messages, list)

#     @pytest.mark.asyncio
#     async def test_get_product_details(self, order_service, setup_test_data):
#         # Test simple read operation
#         product = await order_service.get_product_details("PROD123")
#         assert product.code == "PROD123"

# class TestOrderServiceComplex:
#     '''Test complex operations - UoW'''

#     @pytest.mark.asyncio
#     async def test_process_order_success(
#         self,
#         order_service_with_mocks,
#         sample_order_request,
#         db_assertions
#     ):
#         # Test complex atomic operation
#         result = await order_service_with_mocks.process_order_request(sample_order_request)

#         assert result["success"] is True
#         assert "transaction_id" in result

#         # Verify database state
#         await db_assertions.assert_inbox_exists("REQ001", "completed")
#         inbox = await db_assertions.assert_inbox_exists("REQ001")
#         await db_assertions.assert_transaction_exists(inbox.id, "success")

#     @pytest.mark.asyncio
#     async def test_process_order_rollback_on_error(
#         self,
#         order_service,
#         sample_order_request,
#         db_assertions
#     ):
#         # Mock supplier API to fail
#         with patch('app.services.order_service.OrderService._call_supplier_api') as mock_api:
#             mock_api.side_effect = Exception("Supplier API down")

#             with pytest.raises(HTTPException):
#                 await order_service.process_order_request(sample_order_request)

#             # Verify rollback - no data should exist
#             await db_assertions.assert_tables_empty()

# class TestRepositoryDirect:
#     '''Test repositories directly'''

#     @pytest.mark.asyncio
#     async def test_inbox_repository_crud(self, inbox_repository, sample_inbox_data):
#         # Test direct repository operations
#         inbox = await inbox_repository.create(sample_inbox_data)
#         assert inbox.request_id == "REQ001"

#         found = await inbox_repository.get_by_request_id("REQ001")
#         assert found.id == inbox.id

# class TestUoWIsolation:
#     '''Test UoW transaction isolation'''

#     @pytest.mark.asyncio
#     async def test_uow_commit(self, uow, sample_inbox_data):
#         async with uow:
#             inbox = await uow.inbox.create(sample_inbox_data)
#             await uow.commit()

#         # Verify data persisted
#         found = await uow.inbox.get_by_request_id("REQ001")
#         assert found is not None

#     @pytest.mark.asyncio
#     async def test_uow_rollback(self, uow, sample_inbox_data):
#         try:
#             async with uow:
#                 await uow.inbox.create(sample_inbox_data)
#                 raise Exception("Force rollback")
#         except Exception:
#             pass

#         # Verify data NOT persisted
#         found = await uow.inbox.get_by_request_id("REQ001")
#         assert found is None
# """
