import os
import httpx
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:7000")

security_scheme = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    """
    Validates the token by making an HTTP request to the user_service.
    """
    token = credentials.credentials
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/auth/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token. Please login via user_service."
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error connecting to user_service: {e}"
        )
