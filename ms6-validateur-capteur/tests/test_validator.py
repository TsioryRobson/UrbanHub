import pytest

from src.validator import classify_sensor_value


def test_classifies_normal_value():
    result = classify_sensor_value("c02", 500.0)

    assert result["valid"] is True
    assert result["level"] == "normal"
    assert result["sensor"] == "c02"
    assert result["threshold"] == pytest.approx(800.0)
    assert result["timestamp"]


def test_classifies_moderate_value():
    result = classify_sensor_value("temperature", 35.0)

    assert result["valid"] is True
    assert result["level"] == "moderate"
    assert result["threshold"] == pytest.approx(35.0)


def test_classifies_critical_value():
    result = classify_sensor_value("noise", 85.0)

    assert result["valid"] is False
    assert result["level"] == "critical"
    assert result["threshold"] == pytest.approx(85.0)


def test_supports_extra_humidity_sensor():
    result = classify_sensor_value("humidity", 72.0)

    assert result["valid"] is True
    assert result["level"] == "moderate"
    assert result["threshold"] == pytest.approx(60.0)


def test_rejects_unknown_sensor():
    result = classify_sensor_value("unknown", 10.0)

    assert result["valid"] is False
    assert result["level"] == "unknown"
    assert result["threshold"] is None
    assert result["message"] == "capteur non répértorié"
