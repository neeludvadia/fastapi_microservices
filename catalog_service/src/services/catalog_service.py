from src.interfaces.catalog_repository_interface import ICatalogRepository
from src.dto.product_schema import CreateProductRequest, UpdateProductRequest

class CatalogService:
    def __init__(self, repository: ICatalogRepository, es_service=None):
        self.repository = repository
        self.es_service = es_service
        
    async def create_product(self, input_data: CreateProductRequest):
        data = self.repository.create(input_data)
        if not data.id:
            raise Exception("Unable to create product")
            
        if self.es_service:
            await self.es_service.index_product(data)
        
        # TODO: productsCreatedTotal.inc() (Metrics)
        return data

    async def update_product(self, product_id: int, input_data: UpdateProductRequest):
        data = self.repository.update(product_id, input_data)
        
        if self.es_service:
            await self.es_service.update_product(data)
        
        # TODO: productsUpdatedTotal.inc()
        return data

    async def get_products(self, limit: int, offset: int, search: str = ""):
        if search and self.es_service:
            return await self.es_service.search_products(search)
            
        products = self.repository.find(limit, offset)
        return products

    def get_product(self, product_id: int):
        return self.repository.find_one(product_id)

    async def delete_product(self, product_id: int):
        response = self.repository.delete(product_id)
        
        if self.es_service:
            await self.es_service.delete_product(product_id)
        
        # TODO: productsDeletedTotal.inc()
        return response

    def get_product_stock(self, ids: list[int]):
        products = self.repository.find_stock(ids)
        if not products:
            raise Exception("Unable to find product stock details")
        return products
    
    async def handle_broker_message(self, message: dict):
        event = message.get("event")
        data = message.get("data", {})
        
        if event == "OrderCreated":
            items = data.get("items", [])
            for item in items:
                # Need to update product stock
                try:
                    # In order service, item_name was mistakenly used for product_id.
                    # We updated order service to send product_id in Phase 1.
                    # Fallback to int() parsing if needed.
                    product_id = int(item.get("product_id"))
                    qty = int(item.get("qty"))
                    
                    product = self.get_product(product_id)
                    new_stock = max(0, product.stock - qty)
                    
                    await self.update_product(product_id, UpdateProductRequest(stock=new_stock))
                    print(f"Decreased stock for product {product_id} by {qty}. New stock: {new_stock}")
                except Exception as e:
                    print(f"Error updating stock for product in OrderCreated event: {e}")
                    
# Triggering hot reload
