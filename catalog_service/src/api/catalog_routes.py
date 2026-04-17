from fastapi import APIRouter
from src.dto.product_schema import CreateProductRequest, UpdateProductRequest

# This is equivalent to `const catalogRouter = express.Router();`
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# Equivalent to `catalogRouter.get("/products", async (req, res) => {...})`
@router.get("/")
def get_products(limit: int = 10, offset: int = 0):
    # In FastAPI, query parameters like `limit` and `offset` are automatically
    # extracted from the function arguments! No need for `req.query["limit"]`.
    
    # Dummy data
    return {"message": "List of products", "limit": limit, "offset": offset}

# Equivalent to `catalogRouter.post("/products", ...)`
@router.post("/")
def create_product(product_data: CreateProductRequest):
    # Because of Pydantic, product_data is a fully validated object, not a raw dict!
    # Validation errors (e.g., negative price) return 422 Unprocessable Entity automatically.
    
    # You can access data like: product_data.name, product_data.price
    return {"message": "Product created", "data": product_data.model_dump()}

# Equivalent to `catalogRouter.get("/products/:id", ...)`
@router.get("/{id}")
def get_product(id: int):
    # Path parameters like ":id" are defined with "{id}" in the string
    # and extracted as arguments with type hints!
    return {"message": "Product details", "id": id}

# Equivalent to `catalogRouter.patch("/products/:id", ...)`
@router.patch("/{id}")
def update_product(id: int, product_data: UpdateProductRequest):
    # Notice how we combine both the path parameter (id) and request body (product_data)
    # in the function arguments!
    return {"message": f"Product {id} updated", "data": product_data.model_dump(exclude_unset=True)}

# Equivalent to `catalogRouter.delete("/products/:id", ...)`
@router.delete("/{id}")
def delete_product(id: int):
    return {"message": f"Product {id} deleted", "id": id}

