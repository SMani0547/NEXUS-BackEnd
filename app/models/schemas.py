from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class AskResponse(BaseModel):
    answer: str
    note: str
    data_context: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str
    records_loaded: int

