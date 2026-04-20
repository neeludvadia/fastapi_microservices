import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# This is the FastAPI equivalent of extracting "Bearer <token>" from the header
# In Express you did: const token = req.headers["authorization"]
security_scheme = HTTPBearer()


def create_token(data: dict) -> str:
    """
    Equivalent to the Node.js `generateToken` function:
    jwt.sign(user, process.env.JWT_SECRET)
    """
    to_encode = data.copy()
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """
    Equivalent to the Express /validate route logic.
    FastAPI calls this automatically via Depends() to protect routes.
    
    In Express you did:
      const tokenData = token.split(" ")[1];
      const user = jwt.verify(tokenData, process.env.JWT_SECRET);
    
    FastAPI's HTTPBearer() already extracts the token from "Bearer <token>" for us.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
