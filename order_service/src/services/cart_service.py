from src.repository.cart_repository import CartRepository
from src.dto.cart_schema import CartRequestInput, EditCartRequest
from fastapi import HTTPException, status
import httpx
import os

class CartService:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    async def create_cart(self, customer_id: int, input_data: CartRequestInput):
        # 1. Fetch product details from Catalog Service
        catalog_url = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8000")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{catalog_url}/products/{input_data.product_id}")
                if response.status_code != 200:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
                product = response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=f"Catalog service unavailable: {e}"
            )
            
        # Check stock availability
        stock = product.get("stock", 0)
        if stock < input_data.qty:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of Stock")

        # 2. Get or create cart
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            cart = self.repository.create_cart(customer_id)

        # Check if product already in cart
        line_item = self.repository.find_cart_line_item(cart.id, input_data.product_id)
        if line_item:
            # Check if total quantity after adding exceeds stock
            if stock < (line_item.qty + input_data.qty):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of Stock")
            return self.repository.update_cart_line_item(line_item.id, line_item.qty + input_data.qty)
        else:
            return self.repository.create_cart_line_item(
                cart_id=cart.id,
                product_id=input_data.product_id,
                item_name=product.get("name", input_data.item_name),
                qty=input_data.qty,
                price=product.get("price", input_data.price),
                variant=product.get("variant", input_data.variant)
            )

    async def get_cart(self, customer_id: int):
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
            
        # Extract product IDs in the cart
        product_ids = [item.product_id for item in cart.line_items]
        
        # Call Catalog Service for stock details
        stock_map = {}
        if product_ids:
            try:
                catalog_url = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8000")
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{catalog_url}/products/stock",
                        json={"ids": product_ids}
                    )
                    if response.status_code == 200:
                        products_stock = response.json()
                        stock_map = {p["id"]: p["stock"] for p in products_stock}
            except Exception as e:
                # Log error but don't fail, parity with TS behavior
                print(f"Error fetching stock details: {e}")

        # Map to dict representation containing availability to match TS behavior
        line_items_data = []
        for item in cart.line_items:
            item_dict = {
                "id": item.id,
                "product_id": item.product_id,
                "cart_id": item.cart_id,
                "item_name": item.item_name,
                "variant": item.variant,
                "qty": item.qty,
                "price": item.price,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                "availability": stock_map.get(item.product_id, 0)
            }
            line_items_data.append(item_dict)
            
        cart_data = {
            "id": cart.id,
            "customer_id": cart.customer_id,
            "created_at": cart.created_at.isoformat() if cart.created_at else None,
            "updated_at": cart.updated_at.isoformat() if cart.updated_at else None,
            "line_items": line_items_data
        }
        return cart_data

    async def edit_cart(self, customer_id: int, line_item_id: int, input_data: EditCartRequest):
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        
        # Verify line item belongs to this cart
        line_item = self.repository.find_line_item_by_id(line_item_id)
        if not line_item or line_item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found in cart")
            
        return self.repository.update_cart_line_item(line_item_id, input_data.qty)

    async def delete_cart_item(self, customer_id: int, line_item_id: int):
        cart = self.repository.find_cart_by_customer_id(customer_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        
        line_item = self.repository.find_line_item_by_id(line_item_id)
        if not line_item or line_item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found in cart")
            
        success = self.repository.delete_cart_line_item(line_item_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete item")
        return {"message": "Item deleted successfully"}

