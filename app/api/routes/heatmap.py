from fastapi import APIRouter

from app.api.routes.deps import get_analytics
from app.models.schemas import HeatmapResponse

router = APIRouter(tags=["heatmap"])

@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap() -> HeatmapResponse:
    analytics = get_analytics()
    return HeatmapResponse(**analytics.heatmap())
