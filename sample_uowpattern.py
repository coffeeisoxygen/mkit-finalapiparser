# # ==================== MODELS ====================
# # models.py
# from sqlalchemy import Column, Integer, String, DateTime, JSON, Decimal, ForeignKey, Boolean
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class InboxMessage(Base):
#     __tablename__ = "inbox"

#     id = Column(Integer, primary_key=True, index=True)
#     request_id = Column(String, unique=True, index=True)
#     payload = Column(JSON)
#     status = Column(String, default="received")  # received, processing, completed, failed
#     created_at = Column(DateTime, default=datetime.utcnow)

# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)
#     inbox_id = Column(Integer, ForeignKey("inbox.id"))
#     product_id = Column(String)
#     amount = Column(Decimal(10, 2))
#     status = Column(String, default="pending")  # pending, success, failed, refunded
#     created_at = Column(DateTime, default=datetime.utcnow)

# class OutboxMessage(Base):
#     __tablename__ = "outbox"

#     id = Column(Integer, primary_key=True, index=True)
#     transaction_id = Column(Integer, ForeignKey("transactions.id"))
#     supplier_request = Column(JSON)
#     supplier_response = Column(JSON)
#     status = Column(String, default="pending")  # pending, sent, delivered, failed
#     created_at = Column(DateTime, default=datetime.utcnow)

# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     code = Column(String, unique=True, index=True)
#     name = Column(String)
#     price = Column(Decimal(10, 2))
#     is_available = Column(Boolean, default=True)
#     stock = Column(Integer, default=0)

# # ==================== SCHEMAS ====================
# # schemas.py
# from pydantic import BaseModel
# from datetime import datetime
# from decimal import Decimal
# from typing import Optional, Dict, Any

# class InboxMessageCreate(BaseModel):
#     request_id: str
#     payload: Dict[str, Any]

# class InboxMessageResponse(BaseModel):
#     id: int
#     request_id: str
#     payload: Dict[str, Any]
#     status: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class TransactionCreate(BaseModel):
#     inbox_id: int
#     product_id: str
#     amount: Decimal

# class TransactionResponse(BaseModel):
#     id: int
#     inbox_id: int
#     product_id: str
#     amount: Decimal
#     status: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class ProductResponse(BaseModel):
#     id: int
#     code: str
#     name: str
#     price: Decimal
#     is_available: bool
#     stock: int

#     class Config:
#         from_attributes = True

# # ==================== REPOSITORY INTERFACES ====================
# # repositories/interfaces.py
# from abc import ABC, abstractmethod
# from typing import List, Optional, Dict, Any
# from models import InboxMessage, Transaction, OutboxMessage, Product

# class InboxRepositoryInterface(ABC):
#     @abstractmethod
#     async def create(self, data: Dict[str, Any]) -> InboxMessage:
#         pass

#     @abstractmethod
#     async def get_by_id(self, id: int) -> Optional[InboxMessage]:
#         pass

#     @abstractmethod
#     async def get_by_request_id(self, request_id: str) -> Optional[InboxMessage]:
#         pass

#     @abstractmethod
#     async def get_by_status(self, status: str) -> List[InboxMessage]:
#         pass

#     @abstractmethod
#     async def update(self, id: int, data: Dict[str, Any]) -> Optional[InboxMessage]:
#         pass

# class TransactionRepositoryInterface(ABC):
#     @abstractmethod
#     async def create(self, data: Dict[str, Any]) -> Transaction:
#         pass

#     @abstractmethod
#     async def get_by_id(self, id: int) -> Optional[Transaction]:
#         pass

#     @abstractmethod
#     async def update(self, id: int, data: Dict[str, Any]) -> Optional[Transaction]:
#         pass

# class OutboxRepositoryInterface(ABC):
#     @abstractmethod
#     async def create(self, data: Dict[str, Any]) -> OutboxMessage:
#         pass

#     @abstractmethod
#     async def get_by_id(self, id: int) -> Optional[OutboxMessage]:
#         pass

# class ProductRepositoryInterface(ABC):
#     @abstractmethod
#     async def get_by_id(self, id: int) -> Optional[Product]:
#         pass

#     @abstractmethod
#     async def get_by_code(self, code: str) -> Optional[Product]:
#         pass

# # ==================== REPOSITORY IMPLEMENTATIONS ====================
# # repositories/inbox_repository.py
# from typing import List, Optional, Dict, Any
# from sqlalchemy import select, update
# from sqlalchemy.ext.asyncio import AsyncSession
# from models import InboxMessage
# from repositories.interfaces import InboxRepositoryInterface

# class InboxRepository(InboxRepositoryInterface):
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def create(self, data: Dict[str, Any]) -> InboxMessage:
#         inbox = InboxMessage(**data)
#         self.session.add(inbox)
#         await self.session.flush()  # NO COMMIT - UoW will handle
#         await self.session.refresh(inbox)
#         return inbox

#     async def get_by_id(self, id: int) -> Optional[InboxMessage]:
#         result = await self.session.execute(
#             select(InboxMessage).where(InboxMessage.id == id)
#         )
#         return result.scalar_one_or_none()

#     async def get_by_request_id(self, request_id: str) -> Optional[InboxMessage]:
#         result = await self.session.execute(
#             select(InboxMessage).where(InboxMessage.request_id == request_id)
#         )
#         return result.scalar_one_or_none()

#     async def get_by_status(self, status: str) -> List[InboxMessage]:
#         result = await self.session.execute(
#             select(InboxMessage).where(InboxMessage.status == status)
#         )
#         return result.scalars().all()

#     async def get_all(self, skip: int = 0, limit: int = 100) -> List[InboxMessage]:
#         result = await self.session.execute(
#             select(InboxMessage).offset(skip).limit(limit)
#         )
#         return result.scalars().all()

#     async def update(self, id: int, data: Dict[str, Any]) -> Optional[InboxMessage]:
#         await self.session.execute(
#             update(InboxMessage).where(InboxMessage.id == id).values(**data)
#         )
#         return await self.get_by_id(id)

# # repositories/transaction_repository.py
# from typing import Optional, Dict, Any
# from sqlalchemy import select, update
# from sqlalchemy.ext.asyncio import AsyncSession
# from models import Transaction
# from repositories.interfaces import TransactionRepositoryInterface

# class TransactionRepository(TransactionRepositoryInterface):
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def create(self, data: Dict[str, Any]) -> Transaction:
#         transaction = Transaction(**data)
#         self.session.add(transaction)
#         await self.session.flush()
#         await self.session.refresh(transaction)
#         return transaction

#     async def get_by_id(self, id: int) -> Optional[Transaction]:
#         result = await self.session.execute(
#             select(Transaction).where(Transaction.id == id)
#         )
#         return result.scalar_one_or_none()

#     async def update(self, id: int, data: Dict[str, Any]) -> Optional[Transaction]:
#         await self.session.execute(
#             update(Transaction).where(Transaction.id == id).values(**data)
#         )
#         return await self.get_by_id(id)

# # repositories/outbox_repository.py
# from typing import Optional, Dict, Any
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from models import OutboxMessage
# from repositories.interfaces import OutboxRepositoryInterface

# class OutboxRepository(OutboxRepositoryInterface):
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def create(self, data: Dict[str, Any]) -> OutboxMessage:
#         outbox = OutboxMessage(**data)
#         self.session.add(outbox)
#         await self.session.flush()
#         await self.session.refresh(outbox)
#         return outbox

#     async def get_by_id(self, id: int) -> Optional[OutboxMessage]:
#         result = await self.session.execute(
#             select(OutboxMessage).where(OutboxMessage.id == id)
#         )
#         return result.scalar_one_or_none()

# # repositories/product_repository.py
# from typing import Optional
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from models import Product
# from repositories.interfaces import ProductRepositoryInterface

# class ProductRepository(ProductRepositoryInterface):
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def get_by_id(self, id: int) -> Optional[Product]:
#         result = await self.session.execute(
#             select(Product).where(Product.id == id)
#         )
#         return result.scalar_one_or_none()

#     async def get_by_code(self, code: str) -> Optional[Product]:
#         result = await self.session.execute(
#             select(Product).where(Product.code == code)
#         )
#         return result.scalar_one_or_none()

# # ==================== UNIT OF WORK ====================
# # uow/async_uow.py
# from types import TracebackType
# from sqlalchemy.ext.asyncio import AsyncSession
# from abc import ABC, abstractmethod

# from app.mlogg import logger

# class AbstractUnitOfWork(ABC):
#     @abstractmethod
#     async def commit(self):
#         pass

#     @abstractmethod
#     async def rollback(self):
#         pass

#     async def __aenter__(self):
#         return self

#     async def __aexit__(self, exc_type, exc, tb):
#         if exc_type:
#             await self.rollback()
#         elif not self._committed:
#             await self.commit()

# class AsyncUnitOfWork(AbstractUnitOfWork):
#     def __init__(self, session: AsyncSession):
#         self.session = session
#         self._committed = False
#         with logger.contextualize(uow="AsyncUnitOfWork"):
#             logger.debug("AsyncUnitOfWork initialized")

#     async def __aenter__(self):
#         # Initialize repositories dengan session yang sama
#         self._init_repositories()
#         with logger.contextualize(uow="AsyncUnitOfWork"):
#             logger.debug("UoW entered, repositories initialized")
#         return self

#     def _init_repositories(self):
#         """Initialize semua repositories dengan shared session."""
#         from repositories.inbox_repository import InboxRepository
#         from repositories.transaction_repository import TransactionRepository
#         from repositories.outbox_repository import OutboxRepository
#         from repositories.product_repository import ProductRepository

#         self.inbox = InboxRepository(self.session)
#         self.transactions = TransactionRepository(self.session)
#         self.outbox = OutboxRepository(self.session)
#         self.products = ProductRepository(self.session)

#     async def commit(self):
#         if not self._committed:
#             await self.session.commit()
#             self._committed = True
#             with logger.contextualize(uow="AsyncUnitOfWork"):
#                 logger.info("Transaction committed")

#     async def rollback(self):
#         await self.session.rollback()
#         with logger.contextualize(uow="AsyncUnitOfWork"):
#             logger.info("Transaction rolled back")

#     async def flush(self):
#         """Flush untuk get IDs tanpa commit."""
#         await self.session.flush()
#         with logger.contextualize(uow="AsyncUnitOfWork"):
#             logger.debug("Session flushed")

#     async def __aexit__(
#         self,
#         exc_type: type[BaseException] | None,
#         exc: BaseException | None,
#         tb: TracebackType | None,
#     ):
#         with logger.contextualize(uow="AsyncUnitOfWork"):
#             logger.debug("UoW exiting", exc_type=exc_type, has_exception=exc_type is not None)

#         try:
#             if exc_type:
#                 await self.rollback()
#             elif not self._committed:
#                 await self.commit()
#         except Exception as e:
#             logger.error(f"Error during UoW exit: {e}")
#             if exc_type:
#                 raise exc from e
#             raise e
#         finally:
#             with logger.contextualize(uow="AsyncUnitOfWork"):
#                 logger.debug("UoW exited successfully")

# # ==================== SERVICES ====================
# # services/order_service.py
# from typing import List, Callable
# from fastapi import HTTPException
# import httpx

# from uow.async_uow import AsyncUnitOfWork
# from repositories.interfaces import InboxRepositoryInterface, ProductRepositoryInterface
# from schemas import InboxMessageResponse, ProductResponse, TransactionResponse
# from app.mlogg import logger

# class OrderService:
#     def __init__(
#         self,
#         # Simple repositories untuk direct operations
#         inbox_repo: InboxRepositoryInterface,
#         product_repo: ProductRepositoryInterface,
#         # UoW factory untuk complex operations
#         uow_factory: Callable[[], AsyncUnitOfWork]
#     ):
#         self.inbox_repo = inbox_repo  # Auto-commit repository
#         self.product_repo = product_repo  # Auto-commit repository
#         self.uow_factory = uow_factory

#     # ========== SIMPLE Operations (Direct Repository) ==========
#     async def get_inbox_messages(self, status: str = None) -> List[InboxMessageResponse]:
#         """Simple read - direct repository."""
#         if status:
#             messages = await self.inbox_repo.get_by_status(status)
#         else:
#             messages = await self.inbox_repo.get_all()

#         return [InboxMessageResponse.from_orm(msg) for msg in messages]

#     async def get_inbox_by_request_id(self, request_id: str) -> InboxMessageResponse:
#         """Simple read - direct repository."""
#         message = await self.inbox_repo.get_by_request_id(request_id)
#         if not message:
#             raise HTTPException(404, f"Request {request_id} not found")
#         return InboxMessageResponse.from_orm(message)

#     async def get_product_details(self, product_code: str) -> ProductResponse:
#         """Simple read - direct repository."""
#         product = await self.product_repo.get_by_code(product_code)
#         if not product:
#             raise HTTPException(404, f"Product {product_code} not found")
#         return ProductResponse.from_orm(product)

#     async def update_inbox_status(self, inbox_id: int, status: str) -> InboxMessageResponse:
#         """Simple update - direct repository."""
#         inbox = await self.inbox_repo.update(inbox_id, {"status": status})
#         if not inbox:
#             raise HTTPException(404, "Inbox message not found")
#         return InboxMessageResponse.from_orm(inbox)

#     # ========== COMPLEX Operations (UoW) ==========
#     async def process_order_request(self, request_data: dict) -> dict:
#         """Complex atomic operation - UoW required."""
#         uow = self.uow_factory()

#         async with uow:
#             try:
#                 logger.info(f"Processing order request: {request_data.get('request_id')}")

#                 # Step 1: Check duplicate request
#                 existing = await uow.inbox.get_by_request_id(request_data["request_id"])
#                 if existing:
#                     raise HTTPException(400, "Duplicate request ID")

#                 # Step 2: Save to inbox
#                 inbox_data = {
#                     "request_id": request_data["request_id"],
#                     "payload": request_data,
#                     "status": "processing"
#                 }
#                 inbox = await uow.inbox.create(inbox_data)
#                 await uow.flush()  # Get inbox.id

#                 # Step 3: Validate product
#                 product = await uow.products.get_by_code(request_data["product_id"])
#                 if not product:
#                     raise HTTPException(400, f"Product {request_data['product_id']} not found")
#                 if not product.is_available:
#                     raise HTTPException(400, f"Product {request_data['product_id']} not available")

#                 # Step 4: Create transaction
#                 transaction_data = {
#                     "inbox_id": inbox.id,
#                     "product_id": request_data["product_id"],
#                     "amount": request_data["amount"],
#                     "status": "pending"
#                 }
#                 transaction = await uow.transactions.create(transaction_data)
#                 await uow.flush()  # Get transaction.id

#                 # Step 5: Forward to supplier API
#                 supplier_response = await self._call_supplier_api(request_data)

#                 # Step 6: Save outbox
#                 outbox_data = {
#                     "transaction_id": transaction.id,
#                     "supplier_request": request_data,
#                     "supplier_response": supplier_response,
#                     "status": "delivered" if supplier_response.get("success") else "failed"
#                 }
#                 outbox = await uow.outbox.create(outbox_data)

#                 # Step 7: Update statuses based on supplier response
#                 final_status = "completed" if supplier_response.get("success") else "failed"
#                 transaction_status = "success" if supplier_response.get("success") else "failed"

#                 await uow.inbox.update(inbox.id, {"status": final_status})
#                 await uow.transactions.update(transaction.id, {"status": transaction_status})

#                 logger.info(f"Order processing completed: {transaction.id}")

#                 # UoW auto-commit karena no exception
#                 return {
#                     "success": True,
#                     "transaction_id": transaction.id,
#                     "inbox_id": inbox.id,
#                     "supplier_response": supplier_response
#                 }

#             except HTTPException:
#                 # Business logic errors - re-raise
#                 logger.warning(f"Business logic error in order processing")
#                 raise

#             except httpx.RequestError as e:
#                 # Supplier API errors
#                 logger.error(f"Supplier API error: {e}")
#                 raise HTTPException(502, "Supplier service unavailable")

#             except Exception as e:
#                 # Unexpected errors
#                 logger.error(f"Unexpected error in order processing: {e}")
#                 raise HTTPException(500, "Internal server error")

#     async def handle_refund(self, transaction_id: int) -> dict:
#         """Complex refund operation - UoW required."""
#         uow = self.uow_factory()

#         async with uow:
#             # Get transaction
#             transaction = await uow.transactions.get_by_id(transaction_id)
#             if not transaction:
#                 raise HTTPException(404, "Transaction not found")

#             if transaction.status == "refunded":
#                 raise HTTPException(400, "Transaction already refunded")

#             # Update transaction status
#             await uow.transactions.update(transaction_id, {"status": "refunded"})

#             # Update inbox status
#             await uow.inbox.update(transaction.inbox_id, {"status": "refunded"})

#             # Call refund API
#             refund_response = await self._call_refund_api(transaction_id)

#             # Save refund outbox
#             await uow.outbox.create({
#                 "transaction_id": transaction_id,
#                 "supplier_request": {"action": "refund", "transaction_id": transaction_id},
#                 "supplier_response": refund_response,
#                 "status": "completed"
#             })

#             logger.info(f"Refund processed for transaction: {transaction_id}")
#             return {"refund_processed": True, "transaction_id": transaction_id}

#     # ========== PRIVATE METHODS ==========
#     async def _call_supplier_api(self, request_data: dict) -> dict:
#         """Call external supplier API."""
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "https://supplier-api.com/orders",
#                 json=request_data,
#                 timeout=30
#             )
#             response.raise_for_status()
#             return response.json()

#     async def _call_refund_api(self, transaction_id: int) -> dict:
#         """Call external refund API."""
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 f"https://supplier-api.com/refunds/{transaction_id}",
#                 timeout=30
#             )
#             response.raise_for_status()
#             return response.json()

# # ==================== DEPENDENCIES ====================
# # dependencies.py
# from functools import partial
# from sqlalchemy.ext.asyncio import AsyncSession
# from fastapi import Depends

# from database import get_db_session  # Your existing session manager
# from uow.async_uow import AsyncUnitOfWork
# from repositories.inbox_repository import InboxRepository
# from repositories.product_repository import ProductRepository
# from services.order_service import OrderService

# # Simple repositories dengan auto-commit (untuk simple operations)
# async def get_simple_inbox_repo(session: AsyncSession = Depends(get_db_session)):
#     """Repository untuk simple operations."""
#     repo = InboxRepository(session)
#     # Note: Untuk simple ops, repo akan auto-commit di individual operations
#     return repo

# async def get_simple_product_repo(session: AsyncSession = Depends(get_db_session)):
#     """Repository untuk simple operations."""
#     return ProductRepository(session)

# # UoW factory (untuk complex operations)
# async def get_uow_factory(session: AsyncSession = Depends(get_db_session)):
#     """Factory untuk create UoW instances."""
#     return lambda: AsyncUnitOfWork(session)

# # Service dependency
# async def get_order_service(
#     inbox_repo: InboxRepository = Depends(get_simple_inbox_repo),
#     product_repo: ProductRepository = Depends(get_simple_product_repo),
#     uow_factory = Depends(get_uow_factory)
# ) -> OrderService:
#     """Order service dengan mixed capabilities."""
#     return OrderService(inbox_repo, product_repo, uow_factory)

# # ==================== FASTAPI ROUTER ====================
# # routers/orders.py
# from fastapi import APIRouter, Depends
# from typing import List
# from services.order_service import OrderService
# from dependencies import get_order_service
# from schemas import InboxMessageResponse, ProductResponse

# router = APIRouter(prefix="/orders", tags=["orders"])

# # ========== SIMPLE Endpoints (Direct Repository) ==========
# @router.get("/inbox", response_model=List[InboxMessageResponse])
# async def get_inbox_messages(
#     status: str = None,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Simple read operation - fast response."""
#     return await service.get_inbox_messages(status)

# @router.get("/inbox/{request_id}", response_model=InboxMessageResponse)
# async def get_inbox_by_request_id(
#     request_id: str,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Simple read operation - fast response."""
#     return await service.get_inbox_by_request_id(request_id)

# @router.get("/products/{product_code}", response_model=ProductResponse)
# async def get_product_details(
#     product_code: str,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Simple read operation - fast response."""
#     return await service.get_product_details(product_code)

# @router.patch("/inbox/{inbox_id}/status")
# async def update_inbox_status(
#     inbox_id: int,
#     status: str,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Simple update operation - fast response."""
#     return await service.update_inbox_status(inbox_id, status)

# # ========== COMPLEX Endpoints (UoW) ==========
# @router.post("/process")
# async def process_order_request(
#     request_data: dict,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Complex atomic operation - inbox → transaction → outbox."""
#     return await service.process_order_request(request_data)

# @router.post("/refund/{transaction_id}")
# async def handle_refund(
#     transaction_id: int,
#     service: OrderService = Depends(get_order_service)
# ):
#     """Complex atomic operation - multi-table refund."""
#     return await service.handle_refund(transaction_id)

# # ==================== MAIN APP ====================
# # main.py
# from fastapi import FastAPI
# from routers import orders

# app = FastAPI(title="Order Processing API")

# app.include_router(orders.router)

# @app.on_event("startup")
# async def startup():
#     # Initialize database tables
#     from models import Base
#     from database import sessionmanager

#     async with sessionmanager.connect() as connection:
#         await connection.run_sync(Base.metadata.create_all)

# @app.on_event("shutdown")
# async def shutdown():
#     from database import sessionmanager
#     await sessionmanager.close()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
