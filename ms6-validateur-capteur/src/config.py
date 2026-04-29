from dataclasses import dataclass


@dataclass(frozen=True)
class SensorThreshold:
    moderate: float
    critical: float
    unit: str


SENSOR_THRESHOLDS: dict[str, SensorThreshold] = {
    "c02": SensorThreshold(moderate=800.0, critical=1000.0, unit="ppm"),
    "temperature": SensorThreshold(moderate=35.0, critical=40.0, unit="degC"),
    "noise": SensorThreshold(moderate=70.0, critical=85.0, unit="dB"),
    "pm25": SensorThreshold(moderate=25.0, critical=50.0, unit="ug/m3"),
    "humidity": SensorThreshold(moderate=60.0, critical=80.0, unit="%"),
}
