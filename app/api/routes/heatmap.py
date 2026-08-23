from fastapi import APIRouter, Query

from app.api.routes.deps import get_analytics
from app.models.schemas import HeatmapResponse, YearHeatmapResponse

router = APIRouter(tags=["heatmap"])


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap() -> HeatmapResponse:
    return HeatmapResponse(**get_analytics().heatmap())


@router.get("/heatmap/enhanced", response_model=HeatmapResponse)
def get_enhanced_heatmap(
    product_type: str | None = Query(default=None, alias="type"),
    limit_countries: int = Query(default=20, ge=1, le=40),
    limit_products: int = Query(default=20, ge=1, le=40),
) -> HeatmapResponse:
    return HeatmapResponse(
        **get_analytics().enhanced_heatmap(
            product_type=product_type,
            limit_countries=limit_countries,
            limit_products=limit_products,
        )
    )


@router.get("/heatmap/year", response_model=YearHeatmapResponse)
def get_year_heatmap(
    product: str | None = Query(default=None),
    product_type: str | None = Query(default=None, alias="type"),
) -> YearHeatmapResponse:
    return YearHeatmapResponse(**get_analytics().year_heatmap(product=product, product_type=product_type))

