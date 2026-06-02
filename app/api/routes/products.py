from fastapi import APIRouter, Query

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["products"])


@router.get("/products")
def get_products(product_type: str | None = Query(default=None, alias="type")) -> dict:
    return {"type": product_type, "products": get_analytics().products(product_type)}

