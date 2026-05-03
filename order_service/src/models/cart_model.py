from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

class CartLineItem(SQLModel, table=True):
    __tablename__ = "cart_line_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    cart_id: int = Field(foreign_key="carts.id", ondelete="CASCADE")
    item_name: str
    variant: Optional[str] = None
    qty: int
    price: float # Stored as float/numeric for monetary value
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    cart: "Cart" = Relationship(back_populates="line_items")

class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    line_items: List[CartLineItem] = Relationship(back_populates="cart", cascade_delete=True)
