from typing import Literal

from pydantic import BaseModel, Field


class SensorValidationRequest(BaseModel):
    sensor: str = Field(..., min_length=1, examples=["c02"])
    value: float = Field(..., examples=[500.0])


class SensorValidationResponse(BaseModel):
    valid: bool
    level: Literal["normal", "moderate", "critical", "unknown"]
    sensor: str
    threshold: float | None
    timestamp: str
    message: str | None = None
