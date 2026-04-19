from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.catalog_routes import router as catalog_router
from src.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server boots up (like prisma db push)
    create_db_and_tables()
    yield

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
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
