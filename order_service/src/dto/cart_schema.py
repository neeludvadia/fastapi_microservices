from pydantic import BaseModel
from typing import Optional

class CartItemRequest(BaseModel):
    product_id: int
    qty: int

class CartRequestInput(BaseModel):
    product_id: int
    qty: int
    item_name: str
    price: float
    variant: Optional[str] = None

class EditCartRequest(BaseModel):
    qty: int
