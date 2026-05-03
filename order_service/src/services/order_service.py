import uuid
from fastapi import HTTPException, status
from src.repository.order_repository import OrderRepository
from src.repository.cart_repository import CartRepository
from src.broker.kafka_producer import get_kafka_producer

class OrderService:
    def __init__(self, order_repo: OrderRepository, cart_repo: CartRepository):
        self.order_repo = order_repo
        self.cart_repo = cart_repo

    async def create_order(self, customer_id: int):
        cart = self.cart_repo.find_cart_by_customer_id(customer_id)
        if not cart or not cart.line_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        total_amount = sum(item.price * item.qty for item in cart.line_items)
        
        import random
        order_number = random.randint(100000, 999999) # Generate random order number

        # Create Order
        order = self.order_repo.create_order(
            customer_id=customer_id,
            order_number=order_number,
            amount=total_amount,
            txn_id=None # Set later or pass if exists
        )

        # Create Line Items
        for item in cart.line_items:
            self.order_repo.create_order_line_item(
                order_id=order.id,
                item_name=item.item_name,
                qty=item.qty,
                price=item.price
            )

        # Clear Cart
        self.cart_repo.clear_cart_data(cart.id)
        
        # Emit Kafka OrderCreated event
        producer = get_kafka_producer()
        event_payload = {
            "order_id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "amount": order.amount,
            "items": [
                {
                    "product_id": item.product_id,
                    "qty": item.qty,
                    "price": item.price
                } for item in cart.line_items
            ]
        }
        await producer.send_message("order_events", {"event": "OrderCreated", "data": event_payload})

        return order

    def get_order(self, order_id: int):
        order = self.order_repo.find_order(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    def get_orders(self, customer_id: int):
        return self.order_repo.find_orders_by_customer_id(customer_id)

    def update_order(self, order_id: int, status_str: str):
        order = self.order_repo.update_order_status(order_id, status_str)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return order

    def delete_order(self, order_id: int):
        success = self.order_repo.delete_order(order_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return {"message": "Order deleted successfully"}

    def checkout_order(self, order_number: int):
        order = self.order_repo.find_order_by_number(order_number)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        # Simulate generating a payment link/session
        return {
            "order_number": order.order_number,
            "checkout_url": f"http://localhost:8000/checkout/{order.order_number}",
            "amount": order.amount
        }
