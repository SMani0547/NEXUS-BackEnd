from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    records_loaded: int


# ---------------------------------------------------------------------------
# Summary / Stats (homepage)
# ---------------------------------------------------------------------------

class SummaryResponse(BaseModel):
    total_countries: int
    total_products: int
    total_years: int
    total_records: int
    crop_record_count: int
    livestock_record_count: int


# ---------------------------------------------------------------------------
# Filters (Explorer sidebar)
# ---------------------------------------------------------------------------

class YearRange(BaseModel):
    min: int
    max: int


class FiltersResponse(BaseModel):
    countries: list[str]
    product_types: list[str]
    product_names: list[str]
    year_range: YearRange | None
    years: list[int]
    units: list[str]


# ---------------------------------------------------------------------------
# Data rows (Explorer dataset, Map)
# ---------------------------------------------------------------------------

class YieldRow(BaseModel):
    country: str
    product: str
    type: str
    year: int
    yield_value: float = Field(..., alias="yield")
    unit: str

    model_config = {"populate_by_name": True}


class DataResponse(BaseModel):
    total: int
    rows: list[YieldRow]


# ---------------------------------------------------------------------------
# Trend
# ---------------------------------------------------------------------------

class TrendPoint(BaseModel):
    year: int
    value: float | None


class TrendResponse(BaseModel):
    country: str
    product: str
    type: str
    unit: str
    series: list[TrendPoint]


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

class CountryYield(BaseModel):
    country: str
    unit: str
    value: float | None


class ComparisonResponse(BaseModel):
    product: str
    type: str
    year: int
    countries: list[CountryYield]


# ---------------------------------------------------------------------------
# Country profile (Map detail panel)
# ---------------------------------------------------------------------------

class LatestValue(BaseModel):
    product: str
    type: str
    year: int
    value: float | None
    unit: str


class TrendSummary(BaseModel):
    product: str
    type: str
    direction: str
    change_percent: float | None


class CountryProfileResponse(BaseModel):
    country: str
    available_crop_products: list[str]
    available_livestock_products: list[str]
    years_available: list[int]
    latest_values: list[LatestValue]
    trend_summaries: list[TrendSummary]


# ---------------------------------------------------------------------------
# Heatmap (Explorer heatmap chart)
# ---------------------------------------------------------------------------

class HeatmapCell(BaseModel):
    country: str
    product: str
    avg_yield: float | None
    record_count: int


class HeatmapResponse(BaseModel):
    countries: list[str]
    products: list[str]
    cells: list[HeatmapCell]


# ---------------------------------------------------------------------------
# Insights (Explorer smart stat cards)
# ---------------------------------------------------------------------------

class InsightItem(BaseModel):
    label: str
    value: str
    sub: str


class InsightsResponse(BaseModel):
    highest_yield_country: InsightItem
    fastest_growing_product: InsightItem
    largest_decline_product: InsightItem
    most_reported_product: InsightItem


# ---------------------------------------------------------------------------
# AI Ask
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    note: str
    suggested_questions: list[str] = []
    data_context: dict[str, Any] | None = None
