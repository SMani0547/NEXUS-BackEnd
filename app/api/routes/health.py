from fastapi import APIRouter

from app.api.routes.deps import get_data_service
from app.core.config import get_settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    records_loaded = len(get_data_service().get_data())
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.environment,
        records_loaded=records_loaded,
    )

