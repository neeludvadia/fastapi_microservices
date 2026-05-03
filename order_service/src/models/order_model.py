from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class OrderLineItem(SQLModel, table=True):
    __tablename__ = "order_line_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str
    qty: int
    price: float
    order_id: int = Field(foreign_key="orders.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    order: "Order" = Relationship(back_populates="line_items")

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: int = Field(unique=True, index=True)
    customer_id: int
    amount: float
    status: str = Field(default="pending")
    txn_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    line_items: List[OrderLineItem] = Relationship(back_populates="order", cascade_delete=True)
