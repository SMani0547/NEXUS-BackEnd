from fastapi import APIRouter

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["summary"])


@router.get("/summary")
def get_summary() -> dict:
    return get_analytics().summary()

