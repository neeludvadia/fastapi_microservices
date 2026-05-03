import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.core.database import create_db_and_tables
from src.broker.kafka_producer import get_kafka_producer
from src.api.cart_routes import router as cart_router
from src.api.order_routes import router as order_router

load_dotenv()
APP_PORT = int(os.getenv("APP_PORT", 8002))

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    producer = get_kafka_producer()
    await producer.start()
    yield
    await producer.stop()

app = FastAPI(
    title="Order Service API",
    description="FastAPI equivalent of the Node.js order_service",
    lifespan=lifespan
)

app.include_router(cart_router)
app.include_router(order_router)

@app.get("/health")
def read_health():
    return {"status": "ok", "service": "order_service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=APP_PORT, reload=True)
