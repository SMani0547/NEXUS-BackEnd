from fastapi import APIRouter, Request

from app.api.routes.deps import get_analytics
from app.core.config import get_settings
from app.models.schemas import AskRequest, AskResponse
from app.services.ai_tracking_service import AITrackingService
from app.services.ai_service import AIService

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask_nexus(payload: AskRequest, request: Request) -> AskResponse:
    response = AIService(get_analytics()).answer(payload.question)
    tracker = AITrackingService(get_settings().ai_log_path)
    tracker.record(payload.question, response, _client_metadata(request))
    return AskResponse(**response)


def _client_metadata(request: Request) -> dict[str, str]:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip_address = forwarded_for.split(",")[0].strip()
    if not ip_address:
        ip_address = request.headers.get("x-real-ip", "")
    if not ip_address and request.client:
        ip_address = request.client.host

    user_agent = request.headers.get("user-agent", "")
    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
        "device_type": _device_type(user_agent),
        "country": request.headers.get("cf-ipcountry", ""),
        "city": "",
    }


def _device_type(user_agent: str) -> str:
    value = user_agent.casefold()
    if "ipad" in value or "tablet" in value:
        return "tablet"
    if "mobile" in value or "iphone" in value or "android" in value:
        return "mobile"
    if value:
        return "desktop"
    return "unknown"
