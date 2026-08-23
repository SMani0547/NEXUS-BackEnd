from fastapi import APIRouter, Query

from app.api.routes.deps import get_analytics
from app.models.schemas import RankingsResponse

router = APIRouter(tags=["rankings"])


@router.get("/rankings", response_model=RankingsResponse)
def get_rankings(
    product_type: str | None = Query(default=None, alias="type"),
    year: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> RankingsResponse:
    return RankingsResponse(
        **get_analytics().product_rankings(product_type=product_type, year=year, limit=limit)
    )
