from fastapi import APIRouter

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["countries"])


@router.get("/countries")
def get_countries() -> dict:
    return {"countries": get_analytics().countries()}

