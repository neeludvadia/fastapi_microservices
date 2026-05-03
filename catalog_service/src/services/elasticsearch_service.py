import os
import logging
from elasticsearch import AsyncElasticsearch
from src.models.product_model import Product

logger = logging.getLogger(__name__)

class ElasticSearchService:
    def __init__(self):
        es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.client = AsyncElasticsearch(es_url)
        self.index_name = "products"

    async def setup_index(self):
        try:
            if not await self.client.indices.exists(index=self.index_name):
                await self.client.indices.create(
                    index=self.index_name,
                    mappings={
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "text"},
                            "description": {"type": "text"},
                            "price": {"type": "float"},
                            "stock": {"type": "integer"}
                        }
                    }
                )
                logger.info(f"Created Elasticsearch index: {self.index_name}")
            else:
                logger.info(f"Elasticsearch index '{self.index_name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to setup Elasticsearch index: {repr(e)}")

    async def index_product(self, product: Product):
        try:
            await self.client.index(
                index=self.index_name,
                id=str(product.id),
                document={
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock
                }
            )
        except Exception as e:
            logger.error(f"Error indexing product {product.id}: {e}")

    async def update_product(self, product: Product):
        try:
            await self.client.update(
                index=self.index_name,
                id=str(product.id),
                doc={
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock
                }
            )
        except Exception as e:
            logger.error(f"Error updating product {product.id} in ES: {e}")

    async def delete_product(self, product_id: int):
        try:
            await self.client.delete(
                index=self.index_name,
                id=str(product_id)
            )
        except Exception as e:
            logger.error(f"Error deleting product {product_id} in ES: {e}")

    async def search_products(self, search: str):
        try:
            query = {
                "multi_match": {
                    "query": search,
                    "fields": ["name", "description"]
                }
            }
            response = await self.client.search(
                index=self.index_name,
                query=query
            )
            
            # Map hits to a format that looks like Product instances or dicts
            hits = response["hits"]["hits"]
            return [hit["_source"] for hit in hits]
            
        except Exception as e:
            logger.error(f"Error searching products in ES: {e}")
            return []

    async def close(self):
        await self.client.close()

# Singleton instance
es_service_instance = None

def get_elasticsearch_service() -> ElasticSearchService:
    global es_service_instance
    if es_service_instance is None:
        es_service_instance = ElasticSearchService()
    return es_service_instance
