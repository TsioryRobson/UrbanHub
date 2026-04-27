from fastapi import APIRouter

from src.config import SENSOR_THRESHOLDS
from src.schemas import SensorValidationRequest, SensorValidationResponse
from src.validator import classify_sensor_value

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/thresholds")
def list_thresholds() -> dict[str, dict[str, float | str]]:
    return {
        sensor: {
            "moderate": config.moderate,
            "critical": config.critical,
            "unit": config.unit,
        }
        for sensor, config in SENSOR_THRESHOLDS.items()
    }


@router.post("/validate", response_model=SensorValidationResponse)
def validate_sensor(payload: SensorValidationRequest) -> dict:
    return classify_sensor_value(payload.sensor, payload.value)
