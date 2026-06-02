from fastapi import APIRouter

from app.api.routes.deps import get_analytics
from app.models.schemas import AskRequest, AskResponse
from app.services.ai_service import AIService

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask_nexus(request: AskRequest) -> AskResponse:
    response = AIService(get_analytics()).answer(request.question)
    return AskResponse(**response)

