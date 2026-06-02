from functools import lru_cache

from app.core.config import get_settings
from app.services.analytics_service import AnalyticsService
from app.services.data_service import DataService


@lru_cache(maxsize=1)
def get_data_service() -> DataService:
    """Singleton DataService — CSV is read once and cached for the process lifetime."""
    svc = DataService(get_settings().data_dir)
    svc.get_data()  # warm the in-memory cache on first call
    return svc


def get_analytics() -> AnalyticsService:
    return AnalyticsService(get_data_service().get_data())
