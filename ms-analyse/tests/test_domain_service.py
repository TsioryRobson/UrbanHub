from datetime import datetime, timezone

import pytest

from src.domain.entities import TrafficWindow, VehicleReading
from src.domain.services import TrafficAnalysisService


def build_window(
    *,
    speeds: list[float],
    vehicle_types: list[str],
    vehicle_count: int,
    zone_id: str = "zone-A",
) -> TrafficWindow:
    return TrafficWindow(
        sensor_id="sensor-1",
        zone_id=zone_id,
        window_start=datetime(2026, 4, 11, 10, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2026, 4, 11, 10, 0, 15, tzinfo=timezone.utc),
        vehicles=[
            VehicleReading(speed_kmh=speed, vehicle_type=vehicle_type)
            for speed, vehicle_type in zip(speeds, vehicle_types, strict=True)
        ],
        vehicle_count=vehicle_count,
    )


def test_analyze_returns_low_congestion_and_exact_quality() -> None:
    service = TrafficAnalysisService()
    window = build_window(
        speeds=[50, 55],
        vehicle_types=["car", "car"],
        vehicle_count=2,
    )

    result = service.analyze(window)
    dashboard_payload = result["outputs"][0]["payload"]
    alert_payload = result["outputs"][1]["payload"]
    notification_payload = result["outputs"][3]["payload"]

    assert dashboard_payload["trafficState"] == "low"
    assert dashboard_payload["averageSpeedKmh"] == pytest.approx(52.5)
    assert dashboard_payload["dataQuality"] == "exact"
    assert dashboard_payload["dominantVehicleType"] == "car"
    assert alert_payload["shouldCreateAlert"] is False
    assert alert_payload["alertType"] is None
    assert notification_payload["priority"] == "low"


def test_analyze_returns_high_congestion_and_alert() -> None:
    service = TrafficAnalysisService()
    window = build_window(
        speeds=[10, 15, 20, 22, 18, 12],
        vehicle_types=["car", "truck", "bus", "car", "truck", "car"],
        vehicle_count=12,
        zone_id="zone-B",
    )

    result = service.analyze(window)
    dashboard_payload = result["outputs"][0]["payload"]
    alert_payload = result["outputs"][1]["payload"]
    kpi_payload = result["outputs"][5]["payload"]

    assert dashboard_payload["trafficState"] == "high"
    assert dashboard_payload["dataQuality"] == "estimated"
    assert dashboard_payload["heavyVehicleCount"] == 3
    assert dashboard_payload["slowVehicleCount"] == 6
    assert alert_payload["shouldCreateAlert"] is True
    assert alert_payload["alertType"] == "traffic_congestion"
    assert alert_payload["severity"] == "critical"
    assert kpi_payload["congestionLevel"] == "high"
    assert kpi_payload["heavyVehicleRatio"] == pytest.approx(0.5)


def test_analyze_handles_empty_vehicle_list() -> None:
    service = TrafficAnalysisService()
    window = build_window(speeds=[], vehicle_types=[], vehicle_count=0)

    result = service.analyze(window)
    dashboard_payload = result["outputs"][0]["payload"]
    notification_payload = result["outputs"][3]["payload"]

    assert dashboard_payload["averageSpeedKmh"] == pytest.approx(0.0)
    assert dashboard_payload["minSpeedKmh"] == pytest.approx(0.0)
    assert dashboard_payload["maxSpeedKmh"] == pytest.approx(0.0)
    assert dashboard_payload["dominantVehicleType"] == "unknown"
    assert dashboard_payload["flowRatePerMinute"] == pytest.approx(0.0)
    assert dashboard_payload["trafficState"] == "high"
    assert notification_payload["priority"] == "high"
    assert notification_payload["message"].startswith("Circulation dense")
