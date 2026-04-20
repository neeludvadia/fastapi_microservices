from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from src.core.database import get_session
from src.core.security import verify_token
from src.repository.user_repository import UserRepository
from src.services.user_service import UserService
from src.dto.user_schema import RegisterRequest, LoginRequest

# Equivalent to `const router = express.Router()` + `app.use("/auth", router)`
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ==========================================
# DEPENDENCY INJECTION
# ==========================================
# Same pattern as catalog_service: build the service from the DB session
def get_user_service(session: Session = Depends(get_session)) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)


# ==========================================
# ROUTES
# ==========================================

# Equivalent to: router.post("/register", async (req, res) => { ... })
@router.post("/register", status_code=201)
def register(data: RegisterRequest, service: UserService = Depends(get_user_service)):
    return service.register(data)


# Equivalent to: router.post("/login", async (req, res) => { ... })
@router.post("/login")
def login(data: LoginRequest, response: Response, service: UserService = Depends(get_user_service)):
    result = service.login(data)

    # Set the token in an HTTP-only cookie so the browser sends it automatically
    # httponly=True  → JS cannot access it (prevents XSS token theft)
    # samesite="lax" → sent on same-site requests + top-level navigations (CSRF protection)
    # secure=False   → set to True in production (requires HTTPS)
    response.set_cookie(
        key="access_token",
        value=result["token"],
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return result


# Equivalent to: router.get("/validate", async (req, res) => { ... })
# `verify_token` is a FastAPI dependency — it automatically reads the
# Authorization header and verifies the JWT, just like the Node.js route did.
@router.get("/validate")
def validate(token_data: dict = Depends(verify_token)):
    # If we reach here, the token is valid — return the payload
    # Equivalent to: return res.status(200).json({ ...user as JwtPayload })
    return token_data
