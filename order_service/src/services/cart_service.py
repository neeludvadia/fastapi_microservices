from src.repository.cart_repository import CartRepository
from src.dto.cart_schema import CartRequestInput, EditCartRequest
from fastapi import HTTPException, status

class CartService:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    def create_cart(self, customer_id: int, input_data: CartRequestInput):
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            cart = self.repository.create_cart(customer_id)

        # Check if product already in cart
        line_item = self.repository.find_cart_line_item(cart.id, input_data.product_id)
        if line_item:
            return self.repository.update_cart_line_item(line_item.id, line_item.qty + input_data.qty)
        else:
            return self.repository.create_cart_line_item(
                cart_id=cart.id,
                product_id=input_data.product_id,
                item_name=input_data.item_name,
                qty=input_data.qty,
                price=input_data.price,
                variant=input_data.variant
            )

    def get_cart(self, customer_id: int):
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart

    def edit_cart(self, customer_id: int, line_item_id: int, input_data: EditCartRequest):
        cart = self.get_cart(customer_id)
        
        # Verify line item belongs to this cart
        line_item = self.repository.find_line_item_by_id(line_item_id)
        if not line_item or line_item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found in cart")
            
        return self.repository.update_cart_line_item(line_item_id, input_data.qty)

    def delete_cart_item(self, customer_id: int, line_item_id: int):
        cart = self.get_cart(customer_id)
        
        line_item = self.repository.find_line_item_by_id(line_item_id)
        if not line_item or line_item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found in cart")
            
        success = self.repository.delete_cart_line_item(line_item_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete item")
        return {"message": "Item deleted successfully"}
