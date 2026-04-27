"""Logique metier du microservice ms6-validateur-capteur.

Ce module est volontairement separé des routes FastAPI et de la configuration.
Il contient uniquement les fonctions de validation d'une donnée capteur.

Règles de classification:
- valeur < seuil modéré: niveau "normal"
- seuil modéré <= valeur < seuil critique: niveau "moderate"
- valeur >= seuil critique: niveau "critical"
- capteur inconnu: niveau "unknown" avec un message explicite

La configuration des seuils vient de `src.config.SENSOR_THRESHOLDS`.

Seuils configurés pour ms6-validateur-capteur:

Capteur | Seuil modéré | Seuil critique | Unité
------------------------------------------------
c02 | 800.0 | 1000.0 | ppm
temperature | 35.0 | 40.0 | degC
noise | 70.0 | 85.0 | dB
pm25 | 25.0 | 50.0 | ug/m3
humidity | 60.0 | 80.0 | %
"""

from datetime import datetime, timezone
from typing import Literal

from src.config import SENSOR_THRESHOLDS

Level = Literal["normal", "moderate", "critical", "unknown"]


def normalize_sensor_name(sensor: str) -> str:
    """Normalise le nom du capteur reçu en entrée.

    Cette fonction évite les erreurs simples liées aux espaces ou aux
    majuscules/minuscules. Exemple: " Temperature " devient "temperature".
    """
    return sensor.strip().lower()


def classify_sensor_value(sensor: str, value: float) -> dict:
    """Classe une valeur capteur selon les seuils configurés.

    Args:
        sensor: Nom du capteur reçu, par exemple "c02", "temperature",
            "noise", "pm25" ou "humidity".
        value: Valeur numerique mesurée par le capteur.

    Returns:
        Un dictionnaire prêt à être retourné par l'endpoint POST /validate.

        Pour un capteur connu:
        {
            "valid": bool,
            "level": "normal" | "moderate" | "critical",
            "sensor": str,
            "threshold": float,
            "timestamp": str
        }

        Pour un capteur inconnu:
        {
            "valid": False,
            "level": "unknown",
            "sensor": str,
            "threshold": None,
            "timestamp": str,
            "message": "capteur non répértorié"
        }
    """
    sensor_name = normalize_sensor_name(sensor)
    threshold_config = SENSOR_THRESHOLDS.get(sensor_name)

    if threshold_config is None:
        return {
            "valid": False,
            "level": "unknown",
            "sensor": sensor_name,
            "threshold": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "capteur non répértorié",
        }

    level: Level
    threshold: float
    if value >= threshold_config.critical:
        level = "critical"
        threshold = threshold_config.critical
    elif value >= threshold_config.moderate:
        level = "moderate"
        threshold = threshold_config.moderate
    else:
        level = "normal"
        threshold = threshold_config.moderate

    return {
        "valid": level != "critical",
        "level": level,
        "sensor": sensor_name,
        "threshold": threshold,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_configured_thresholds() -> list[dict[str, float | str]]:
    """Retourne la liste des seuils configurés pour le livrable.

    Cette fonction permet d'afficher clairement la configuration utilisée par
    la logique metier sans passer par FastAPI.
    """
    return [
        {
            "sensor": sensor,
            "moderate_threshold": config.moderate,
            "critical_threshold": config.critical,
            "unit": config.unit,
        }
        for sensor, config in SENSOR_THRESHOLDS.items()
    ]


def display_configured_thresholds() -> None:
    """Affiche les seuils configurés dans la console."""
    print("Seuils configurés pour ms6-validateur-capteur")
    print("Capteur | Seuil modéré | Seuil critique | Unité")
    print("-" * 55)
    for item in get_configured_thresholds():
        print(
            f"{item['sensor']} | "
            f"{item['moderate_threshold']} | "
            f"{item['critical_threshold']} | "
            f"{item['unit']}"
        )


if __name__ == "__main__":
    display_configured_thresholds()
