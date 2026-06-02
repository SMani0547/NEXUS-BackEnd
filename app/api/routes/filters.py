from fastapi import APIRouter

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["filters"])


@router.get("/filters")
def get_filters() -> dict:
    return get_analytics().filters()

