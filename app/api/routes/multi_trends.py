from fastapi import APIRouter, Query

from app.api.routes.deps import get_analytics
from app.models.schemas import MultiTrendsResponse

router = APIRouter(tags=["multi-trends"])


@router.get("/multi-trends", response_model=MultiTrendsResponse)
def get_multi_trends(
    product: str = Query(...),
    countries: str | None = Query(default=None, description="Comma-separated country names"),
    year_min: int | None = Query(default=None),
    year_max: int | None = Query(default=None),
    product_type: str | None = Query(default=None, alias="type"),
) -> MultiTrendsResponse:
    country_list = [item.strip() for item in countries.split(",") if item.strip()] if countries else None
    return MultiTrendsResponse(
        **get_analytics().multi_country_trend(
            product=product,
            countries=country_list,
            year_min=year_min,
            year_max=year_max,
            product_type=product_type,
        )
    )
