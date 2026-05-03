import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.api.auth_routes import router as auth_router
from src.core.database import create_db_and_tables
from src.core.rate_limiter import get_redis_client, close_redis_client

load_dotenv()
APP_PORT = int(os.getenv("APP_PORT", 7000))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server boots up
    create_db_and_tables()
    
    # Initialize Redis connection for rate limiting
    await get_redis_client()
    
    yield
    
    # Cleanup Redis connection
    await close_redis_client()

# Equivalent to `const app = express()`
app = FastAPI(
    title="User Service API",
    description="FastAPI equivalent of the Node.js user_service. Handles auth: register, login, validate.",
    version="1.0.0",
    lifespan=lifespan
)

# Equivalent to `app.use("/auth", rateLimiter, authRoutes)`
# (rate limiter will be added later)
app.include_router(auth_router)

# Health check — equivalent to a simple res.json({ status: "ok" })
@app.get("/health")
def health():
    return {"status": "ok", "service": "user_service"}

if __name__ == "__main__":
    import uvicorn
    # Equivalent to `app.listen(PORT, () => console.log(...))`
    uvicorn.run("main:app", host="127.0.0.1", port=APP_PORT, reload=True)
