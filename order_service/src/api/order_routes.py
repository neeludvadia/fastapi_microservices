from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from src.core.database import get_session
from src.core.security import verify_token
from src.repository.order_repository import OrderRepository
from src.repository.cart_repository import CartRepository
from src.services.order_service import OrderService
from src.dto.order_schema import UpdateOrderStatusRequest

router = APIRouter(
    tags=["Orders"]
)

def get_order_service(session: Session = Depends(get_session)) -> OrderService:
    order_repo = OrderRepository(session)
    cart_repo = CartRepository(session)
    return OrderService(order_repo, cart_repo)

@router.post("/orders")
async def create_order(
    token_data: dict = Depends(verify_token),
    service: OrderService = Depends(get_order_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    if not customer_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    return await service.create_order(int(customer_id))

@router.get("/order/{id}")
def get_order(
    id: int,
    token_data: dict = Depends(verify_token),
    service: OrderService = Depends(get_order_service)
):
    # Depending on auth model, we should verify the order belongs to the user
    # For now, parity with node code
    return service.get_order(id)

@router.get("/orders/{id}")
def get_order_alt(
    id: int,
    token_data: dict = Depends(verify_token),
    service: OrderService = Depends(get_order_service)
):
    return service.get_order(id)

@router.get("/orders")
def get_orders(
    token_data: dict = Depends(verify_token),
    service: OrderService = Depends(get_order_service)
):
    customer_id = token_data.get("sub") or token_data.get("id")
    return service.get_orders(int(customer_id))

@router.patch("/order/{id}")
def update_order(
    id: int,
    data: UpdateOrderStatusRequest,
    token_data: dict = Depends(verify_token), # Only microservices should call this in reality
    service: OrderService = Depends(get_order_service)
):
    return service.update_order(id, data.status)

@router.delete("/order/{id}")
def delete_order(
    id: int,
    token_data: dict = Depends(verify_token),
    service: OrderService = Depends(get_order_service)
):
    return service.delete_order(id)

@router.get("/orders/{id}/checkout")
def checkout_order(
    id: int,
    # No auth in node js for this route, so omitted here
    service: OrderService = Depends(get_order_service)
):
    return service.checkout_order(id)
