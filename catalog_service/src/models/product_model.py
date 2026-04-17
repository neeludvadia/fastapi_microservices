from sqlmodel import SQLModel, Field
from typing import Optional

# This replaces your Prisma model:
# model Product {
#   id Int @id @default(autoincrement())
#   name String
#   description String
#   price Float
#   stock Int
# }

class Product(SQLModel, table=True):
    # Field(primary_key=True) handles the @id and @default(autoincrement())
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # By default, SQLModel fields map directly to columns
    name: str = Field(index=True)  # Added an index to make searches faster
    description: str
    price: float
    stock: int

