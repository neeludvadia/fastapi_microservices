from fastapi import FastAPI
from src.api.catalog_routes import router as catalog_router

# This is analogous to "const app = express();"
app = FastAPI(
    title="Catalog Service API",
    description="This is the FastAPI equivalent of the Node.js catalog_service"
)

# This is analogous to "app.use(catalogRouter)"
app.include_router(catalog_router)

# This is analogous to "app.get('/health', (req, res) => res.json({...}))"
@app.get("/health")
def read_health():
    return {"status": "ok", "service": "catalog_service"}
