from fastapi import APIRouter, Query, Response
from typing import Optional

from app.api.routes.deps import get_analytics
from app.models.schemas import DataResponse, YieldRow

router = APIRouter(tags=["data"])

@router.get("/data", response_model=DataResponse)
def get_data(
    type: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
) -> DataResponse:
    analytics = get_analytics()
    rows = analytics.data_rows(
        type_filter=type,
        country=country,
        product=product,
        year_min=year_min,
        year_max=year_max
    )
    return DataResponse(total=len(rows), rows=[YieldRow(**r) for r in rows])

@router.get("/data/export")
def export_data(
    type: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
):
    analytics = get_analytics()
    # data_rows just returns dicts, let's get the dataframe filtered
    df = analytics.data
    if type and type.casefold() != "all":
        df = df[df["type"].str.casefold() == type.casefold()]
    if country and country.casefold() != "all":
        df = df[df["country"].str.casefold() == country.casefold()]
    if product and product.casefold() != "all":
        df = df[df["product"].str.casefold() == product.casefold()]
    if year_min is not None:
        df = df[df["year"] >= year_min]
    if year_max is not None:
        df = df[df["year"] <= year_max]
        
    csv_data = df.to_csv(index=False)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=nexus_data.csv"}
    )
