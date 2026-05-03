from sqlmodel import Session, select
from src.models.order_model import Order, OrderLineItem
from typing import List, Optional

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_order(self, customer_id: int, order_number: int, amount: float, txn_id: str = None) -> Order:
        order = Order(
            customer_id=customer_id,
            order_number=order_number,
            amount=amount,
            txn_id=txn_id
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def create_order_line_item(self, order_id: int, item_name: str, qty: int, price: float) -> OrderLineItem:
        line_item = OrderLineItem(
            order_id=order_id,
            item_name=item_name,
            qty=qty,
            price=price
        )
        self.session.add(line_item)
        self.session.commit()
        self.session.refresh(line_item)
        return line_item

    def find_order(self, order_id: int) -> Optional[Order]:
        return self.session.get(Order, order_id)

    def find_order_by_number(self, order_number: int) -> Optional[Order]:
        statement = select(Order).where(Order.order_number == order_number)
        return self.session.exec(statement).first()

    def find_orders_by_customer_id(self, customer_id: int) -> List[Order]:
        statement = select(Order).where(Order.customer_id == customer_id)
        return self.session.exec(statement).all()

    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        order = self.find_order(order_id)
        if order:
            order.status = status
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)
        return order

    def delete_order(self, order_id: int) -> bool:
        order = self.find_order(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()
            return True
        return False
