from abc import ABC, abstractmethod
from typing import List
from src.models.product_model import Product
from src.dto.product_schema import CreateProductRequest, UpdateProductRequest

# This replaces export interface IcatalogRepository
class ICatalogRepository(ABC):
    
    @abstractmethod
    def create(self, data: CreateProductRequest) -> Product:
        pass

    @abstractmethod
    def update(self, product_id: int, data: UpdateProductRequest) -> Product:
        pass

    @abstractmethod
    def delete(self, product_id: int):
        pass

    @abstractmethod
    def find(self, limit: int, offset: int) -> List[Product]:
        pass

    @abstractmethod
    def find_one(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def find_stock(self, ids: List[int]) -> List[Product]:
        pass
