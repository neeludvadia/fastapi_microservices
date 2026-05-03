from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.core.database import get_session
from src.core.security import verify_token
from src.repository.cart_repository import CartRepository
from src.services.cart_service import CartService
from src.dto.cart_schema import CartRequestInput, EditCartRequest
from src.core.rate_limiter import rate_limiter

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
    dependencies=[Depends(verify_token), Depends(rate_limiter(max_requests=30, window_seconds=60))]
)

def get_cart_service(session: Session = Depends(get_session)) -> CartService:
    repository = CartRepository(session)
    return CartService(repository)

@router.post("")
def add_to_cart(
    data: CartRequestInput,
    token_data: dict = Depends(verify_token),
    service: CartService = Depends(get_cart_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    if not customer_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    response = service.create_cart(int(customer_id), data)
    return response

@router.get("")
def get_cart(
    token_data: dict = Depends(verify_token),
    service: CartService = Depends(get_cart_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    response = service.get_cart(int(customer_id))
    return response

@router.patch("/{line_item_id}")
def update_cart_item(
    line_item_id: int,
    data: EditCartRequest,
    token_data: dict = Depends(verify_token),
    service: CartService = Depends(get_cart_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    response = service.edit_cart(int(customer_id), line_item_id, data)
    return response

@router.delete("/{line_item_id}")
def delete_cart_item(
    line_item_id: int,
    token_data: dict = Depends(verify_token),
    service: CartService = Depends(get_cart_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    response = service.delete_cart_item(int(customer_id), line_item_id)
    return response
