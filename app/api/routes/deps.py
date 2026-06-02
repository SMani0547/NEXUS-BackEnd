from app.core.config import get_settings
from app.services.analytics_service import AnalyticsService
from app.services.data_service import DataService


def get_data_service() -> DataService:
    return DataService(get_settings().data_dir)


def get_analytics() -> AnalyticsService:
    data = get_data_service().get_data()
    return AnalyticsService(data)

