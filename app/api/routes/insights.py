from fastapi import APIRouter, Query
from typing import Optional

from app.api.routes.deps import get_analytics
from app.models.schemas import InsightsResponse

router = APIRouter(tags=["insights"])

@router.get("/insights", response_model=InsightsResponse)
def get_insights(
    product: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
) -> InsightsResponse:
    analytics = get_analytics()
    return InsightsResponse(**analytics.insights(product=product, year_min=year_min, year_max=year_max))
