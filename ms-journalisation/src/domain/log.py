"""
Entité métier Log
Représente un événement qui doit être journalisé
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class LogLevel(Enum):
    """Énumération des niveaux de log"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL"


class Log:
    """Entité métier Log"""

    def __init__(
        self,
        service: str,
        event_type: str,
        message: str,
        level: str = "INFO",
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        log_id: Optional[str] = None
    ):
        """
        Initialise un log

        Args:
            service: Nom du microservice source
            event_type: Type d'événement
            message: Message du log
            level: Niveau de log (INFO, WARNING, ERROR, etc.)
            timestamp: Timestamp du log
            metadata: Métadonnées additionnelles
            log_id: Identifiant du log
        """
        self.log_id = log_id
        self.service = service
        self.event_type = event_type
        self.message = message
        self.level = level
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return (
            f"Log(id={self.log_id}, service={self.service}, "
            f"event_type={self.event_type}, level={self.level})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le log en dictionnaire"""
        return {
            "id": self.log_id,
            "service": self.service,
            "event_type": self.event_type,
            "message": self.message,
            "level": self.level,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Log":
        """Crée un log à partir d'un dictionnaire"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return Log(
            service=data.get("service", ""),
            event_type=data.get("event_type", ""),
            message=data.get("message", ""),
            level=data.get("level", "INFO"),
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
            log_id=data.get("id")
        )
