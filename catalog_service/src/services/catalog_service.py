from src.interfaces.catalog_repository_interface import ICatalogRepository
from src.dto.product_schema import CreateProductRequest, UpdateProductRequest

class CatalogService:
    def __init__(self, repository: ICatalogRepository):
        self.repository = repository
        
    def create_product(self, input_data: CreateProductRequest):
        data = self.repository.create(input_data)
        if not data.id:
            raise Exception("Unable to create product")
            
        # TODO: emit event to create record in Elastic Search
        # AppEventListener.instance.notify(...)
        
        # TODO: productsCreatedTotal.inc() (Metrics)
        return data

    def update_product(self, product_id: int, input_data: UpdateProductRequest):
        data = self.repository.update(product_id, input_data)
        
        # TODO: emit event to update record in Elastic search
        
        # TODO: productsUpdatedTotal.inc()
        return data

    def get_products(self, limit: int, offset: int, search: str = ""):
        # Later: get products from elastic search
        # elkService = ElasticSearchService()
        # products = elkService.searchProduct(search)
        
        # For now, bypassing elastic search directly to DB to get something working:
        products = self.repository.find(limit, offset)
        return products

    def get_product(self, product_id: int):
        return self.repository.find_one(product_id)

    def delete_product(self, product_id: int):
        response = self.repository.delete(product_id)
        
        # TODO: delete record from elastic search 
        
        # TODO: productsDeletedTotal.inc()
        return response

    def get_product_stock(self, ids: list[int]):
        products = self.repository.find_stock(ids)
        if not products:
            raise Exception("Unable to find product stock details")
        return products
    
    def handle_broker_message(self, message: dict):
        # We will implement Kafka logic later!
        pass
