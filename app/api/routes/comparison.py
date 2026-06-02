from fastapi import APIRouter, HTTPException, Query

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["comparison"])


@router.get("/comparison")
def get_comparison(
    product: str = Query(...),
    year: int = Query(...),
    product_type: str | None = Query(default=None, alias="type"),
) -> dict:
    result = get_analytics().comparison(product=product, year=year, product_type=product_type)
    if not result["countries"]:
        raise HTTPException(status_code=404, detail="No comparison data found for those filters.")
    return result

