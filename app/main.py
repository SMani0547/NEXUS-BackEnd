from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, comparison, countries, country_profile, filters, health, products, summary, trends
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for NEXUS Pacific agriculture data visualizations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(summary.router, prefix=settings.api_prefix)
app.include_router(countries.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(filters.router, prefix=settings.api_prefix)
app.include_router(trends.router, prefix=settings.api_prefix)
app.include_router(comparison.router, prefix=settings.api_prefix)
app.include_router(country_profile.router, prefix=settings.api_prefix)
app.include_router(ask.router, prefix=settings.api_prefix)

