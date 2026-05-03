import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.api.catalog_routes import router as catalog_router
from src.core.database import create_db_and_tables
from src.broker.kafka_consumer import get_kafka_consumer
from src.services.elasticsearch_service import get_elasticsearch_service
from src.core.rate_limiter import get_redis_client, close_redis_client

load_dotenv()
APP_PORT = int(os.getenv("APP_PORT", 8001))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server boots up (like prisma db push)
    create_db_and_tables()
    
    es_service = get_elasticsearch_service()
    await es_service.setup_index()
    
    consumer = get_kafka_consumer()
    await consumer.start()
    
    # Initialize Redis connection for rate limiting
    await get_redis_client()
    
    yield
    
    await consumer.stop()
    await es_service.close()
    await close_redis_client()

# This is analogous to "const app = express();"
app = FastAPI(
    title="Catalog Service API",
    description="This is the FastAPI equivalent of the Node.js catalog_service",
    lifespan=lifespan
)

# This is analogous to "app.use(catalogRouter)"
app.include_router(catalog_router)

# This is analogous to "app.get('/health', (req, res) => res.json({...}))"
@app.get("/health")
def read_health():
    return {"status": "ok", "service": "catalog_service"}

if __name__ == "__main__":
    import uvicorn
    # This acts like `app.listen(8001, ...)` in Express
    uvicorn.run("main:app", host="127.0.0.1", port=APP_PORT, reload=True)
