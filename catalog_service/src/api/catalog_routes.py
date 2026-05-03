from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.core.database import get_session
from src.repository.catalog_repository import CatalogRepository
from src.services.catalog_service import CatalogService
from src.services.elasticsearch_service import get_elasticsearch_service
from src.dto.product_schema import CreateProductRequest, UpdateProductRequest
from src.core.security import verify_token

# This is equivalent to `const catalogRouter = express.Router();`
router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(verify_token)]
)

# ==========================================
# DEPENDENCY INJECTION
# ==========================================
# This function tells FastAPI how to build the CatalogService.
# It uses Depends(get_session) to get a fresh DB session for the request,
# passes it to the repository, and returns the finished service.
def get_catalog_service(session: Session = Depends(get_session)) -> CatalogService:
    repository = CatalogRepository(session)
    es_service = get_elasticsearch_service()
    return CatalogService(repository, es_service)


# ==========================================
# ROUTES
# ==========================================

# By adding `service: CatalogService = Depends(get_catalog_service)`,
# FastAPI automatically runs our dependency builder and gives us the service!
@router.post("/")
async def create_product(
    product_data: CreateProductRequest, 
    service: CatalogService = Depends(get_catalog_service)
):
    # The service connects to the repository, which uses SQLModel to insert to Postgres!
    created_item = await service.create_product(product_data)
    return {"message": "Product created", "data": created_item}


@router.get("/")
async def get_products(
    limit: int = 10, 
    offset: int = 0, 
    search: str = "",
    service: CatalogService = Depends(get_catalog_service)
):
    return await service.get_products(limit, offset, search)


@router.get("/{id}")
def get_product(id: int, service: CatalogService = Depends(get_catalog_service)):
    return service.get_product(id)


@router.patch("/{id}")
async def update_product(
    id: int, 
    product_data: UpdateProductRequest, 
    service: CatalogService = Depends(get_catalog_service)
):
    updated_item = await service.update_product(id, product_data)
    return {"message": f"Product {id} updated", "data": updated_item}


@router.delete("/{id}")
async def delete_product(id: int, service: CatalogService = Depends(get_catalog_service)):
    deleted_item = await service.delete_product(id)
    return {"message": f"Product {id} deleted", "data": deleted_item}
