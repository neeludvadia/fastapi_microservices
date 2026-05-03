from sqlmodel import Session, select
from src.models.cart_model import Cart, CartLineItem
from typing import Optional

class CartRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_cart(self, customer_id: int) -> Cart:
        cart = Cart(customer_id=customer_id)
        self.session.add(cart)
        self.session.commit()
        self.session.refresh(cart)
        return cart

    def find_cart_by_customer_id(self, customer_id: int) -> Optional[Cart]:
        statement = select(Cart).where(Cart.customer_id == customer_id)
        return self.session.exec(statement).first()

    def create_cart_line_item(self, cart_id: int, product_id: int, item_name: str, qty: int, price: float, variant: str = None) -> CartLineItem:
        line_item = CartLineItem(
            cart_id=cart_id,
            product_id=product_id,
            item_name=item_name,
            qty=qty,
            price=price,
            variant=variant
        )
        self.session.add(line_item)
        self.session.commit()
        self.session.refresh(line_item)
        return line_item

    def find_cart_line_item(self, cart_id: int, product_id: int) -> Optional[CartLineItem]:
        statement = select(CartLineItem).where(
            CartLineItem.cart_id == cart_id,
            CartLineItem.product_id == product_id
        )
        return self.session.exec(statement).first()
        
    def find_line_item_by_id(self, line_item_id: int) -> Optional[CartLineItem]:
        return self.session.get(CartLineItem, line_item_id)

    def update_cart_line_item(self, line_item_id: int, qty: int) -> CartLineItem:
        line_item = self.find_line_item_by_id(line_item_id)
        if line_item:
            line_item.qty = qty
            self.session.add(line_item)
            self.session.commit()
            self.session.refresh(line_item)
        return line_item

    def delete_cart_line_item(self, line_item_id: int) -> bool:
        line_item = self.find_line_item_by_id(line_item_id)
        if line_item:
            self.session.delete(line_item)
            self.session.commit()
            return True
        return False

    def clear_cart_data(self, cart_id: int) -> bool:
        cart = self.session.get(Cart, cart_id)
        if cart:
            for item in cart.line_items:
                self.session.delete(item)
            self.session.delete(cart)
            self.session.commit()
            return True
        return False
