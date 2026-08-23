from fastapi import APIRouter

from app.api.routes.deps import get_analytics
from app.models.schemas import TypeSummaryResponse

router = APIRouter(tags=["type-summary"])


@router.get("/type-summary", response_model=TypeSummaryResponse)
def get_type_summary() -> TypeSummaryResponse:
    return TypeSummaryResponse(**get_analytics().type_summary())
