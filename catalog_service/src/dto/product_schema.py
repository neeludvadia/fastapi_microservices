from pydantic import BaseModel, Field
from typing import Optional

# Equivalent to TypeScript CreateProductRequest interface + class-validator
class CreateProductRequest(BaseModel):
    name: str = Field(..., description="Product name", min_length=1)
    description: str = Field(..., description="Product description")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: int = Field(..., ge=0, description="Stock cannot be negative")

# Equivalent to TypeScript UpdateProductRequest interface
# All fields are Optional because it's a PATCH request
class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, description="Product name", min_length=1)
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[float] = Field(None, gt=0, description="Price must be greater than 0")
    stock: Optional[int] = Field(None, ge=0, description="Stock cannot be negative")
