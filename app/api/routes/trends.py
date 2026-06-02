from fastapi import APIRouter, HTTPException, Query

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["trends"])


@router.get("/trends")
def get_trend(
    country: str = Query(...),
    product: str = Query(...),
    product_type: str | None = Query(default=None, alias="type"),
) -> dict:
    result = get_analytics().trend(country=country, product=product, product_type=product_type)
    if not result["series"]:
        raise HTTPException(status_code=404, detail="No trend data found for those filters.")
    return result

