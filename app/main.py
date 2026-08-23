from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.api.routes import ask, comparison, countries, country_profile, filters, health, products, summary, trends, data, heatmap, insights, type_summary, multi_trends, rankings
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def read_root():
    html_path = Path("app/static/index.html")
    return html_path.read_text(encoding="utf-8")

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(summary.router, prefix=settings.api_prefix)
app.include_router(countries.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(filters.router, prefix=settings.api_prefix)
app.include_router(trends.router, prefix=settings.api_prefix)
app.include_router(comparison.router, prefix=settings.api_prefix)
app.include_router(country_profile.router, prefix=settings.api_prefix)
app.include_router(ask.router, prefix=settings.api_prefix)
app.include_router(data.router, prefix=settings.api_prefix)
app.include_router(heatmap.router, prefix=settings.api_prefix)
app.include_router(insights.router, prefix=settings.api_prefix)
app.include_router(type_summary.router, prefix=settings.api_prefix)
app.include_router(multi_trends.router, prefix=settings.api_prefix)
app.include_router(rankings.router, prefix=settings.api_prefix)

