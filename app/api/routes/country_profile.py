from fastapi import APIRouter, HTTPException, Query

from app.api.routes.deps import get_analytics

router = APIRouter(tags=["country-profile"])


@router.get("/country-profile")
def get_country_profile(country: str = Query(...)) -> dict:
    result = get_analytics().country_profile(country)
    if not result["years_available"]:
        raise HTTPException(status_code=404, detail="No country profile data found.")
    return result

