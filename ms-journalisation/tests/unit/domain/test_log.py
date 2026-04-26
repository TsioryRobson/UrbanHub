"""
Tests unitaires pour l'entité Log
"""
import pytest
from datetime import datetime
from src.domain.log import Log, LogLevel


class TestLogEntity:
    """Tests pour l'entité Log"""

    def test_log_creation_with_defaults(self):
        """Test la création d'un log avec les valeurs par défaut"""
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé avec succès"
        )

        assert log.service == "MS Alerte"
        assert log.event_type == "notification_sent"
        assert log.message == "Email envoyé avec succès"
        assert log.level == "INFO"
        assert log.timestamp is not None
        assert isinstance(log.timestamp, datetime)
        assert log.metadata == {}

    def test_log_creation_with_all_parameters(self):
        """Test la création d'un log avec tous les paramètres"""
        timestamp = datetime(2026, 4, 21, 10, 0, 0)
        metadata = {"user_id": "123", "request_id": "456"}

        log = Log(
            service="MS Analyse",
            event_type="analysis_completed",
            message="Analyse complétée",
            level="ERROR",
            timestamp=timestamp,
            metadata=metadata,
            log_id="log-001"
        )

        assert log.log_id == "log-001"
        assert log.service == "MS Analyse"
        assert log.event_type == "analysis_completed"
        assert log.message == "Analyse complétée"
        assert log.level == "ERROR"
        assert log.timestamp == timestamp
        assert log.metadata == metadata

    def test_log_repr(self):
        """Test la représentation textuelle du log"""
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé",
            log_id="log-123"
        )

        repr_str = repr(log)
        assert "log-123" in repr_str
        assert "MS Alerte" in repr_str
        assert "notification_sent" in repr_str

    def test_log_to_dict(self):
        """Test la conversion du log en dictionnaire"""
        timestamp = datetime(2026, 4, 21, 10, 0, 0)
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé",
            level="INFO",
            timestamp=timestamp,
            metadata={"key": "value"},
            log_id="log-001"
        )

        log_dict = log.to_dict()

        assert log_dict["id"] == "log-001"
        assert log_dict["service"] == "MS Alerte"
        assert log_dict["event_type"] == "notification_sent"
        assert log_dict["message"] == "Email envoyé"
        assert log_dict["level"] == "INFO"
        assert log_dict["timestamp"] == timestamp.isoformat()
        assert log_dict["metadata"] == {"key": "value"}

    def test_log_from_dict(self):
        """Test la création d'un log à partir d'un dictionnaire"""
        log_dict = {
            "id": "log-001",
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé",
            "level": "INFO",
            "timestamp": "2026-04-21T10:00:00",
            "metadata": {"key": "value"}
        }

        log = Log.from_dict(log_dict)

        assert log.log_id == "log-001"
        assert log.service == "MS Alerte"
        assert log.event_type == "notification_sent"
        assert log.message == "Email envoyé"
        assert log.level == "INFO"
        assert log.metadata == {"key": "value"}

    def test_log_from_dict_minimal(self):
        """Test la création d'un log à partir d'un dictionnaire minimal"""
        log_dict = {
            "service": "MS Analyse",
            "event_type": "analysis_completed",
            "message": "Analyse complétée"
        }

        log = Log.from_dict(log_dict)

        assert log.service == "MS Analyse"
        assert log.event_type == "analysis_completed"
        assert log.message == "Analyse complétée"
        assert log.level == "INFO"
        assert log.log_id is None

    def test_log_metadata_manipulation(self):
        """Test la manipulation des métadonnées"""
        log = Log(
            service="MS Test",
            event_type="test_event",
            message="Test message"
        )

        # Ajouter une métadonnée
        log.metadata["custom_field"] = "custom_value"
        assert log.metadata["custom_field"] == "custom_value"

        # Vérifier que la métadonnée est présente dans to_dict
        log_dict = log.to_dict()
        assert log_dict["metadata"]["custom_field"] == "custom_value"

    def test_log_level_enum(self):
        """Test l'énumération LogLevel"""
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_different_levels(self):
        """Test la création de logs avec différents niveaux"""
        levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]

        for level in levels:
            log = Log(
                service="MS Test",
                event_type="test_event",
                message="Test message",
                level=level
            )
            assert log.level == level

    def test_log_timestamp_defaults_to_now(self):
        """Test que le timestamp par défaut est maintenant"""
        before = datetime.now()
        log = Log(
            service="MS Test",
            event_type="test_event",
            message="Test message"
        )
        after = datetime.now()

        assert before <= log.timestamp <= after

    def test_log_with_empty_metadata(self):
        """Test la création d'un log avec des métadonnées vides"""
        log = Log(
            service="MS Test",
            event_type="test_event",
            message="Test message",
            metadata={}
        )

        assert log.metadata == {}

    def test_log_from_dict_with_datetime_object(self):
        """Test la création d'un log à partir d'un dictionnaire avec datetime"""
        timestamp = datetime(2026, 4, 21, 10, 0, 0)
        log_dict = {
            "service": "MS Test",
            "event_type": "test_event",
            "message": "Test message",
            "timestamp": timestamp
        }

        log = Log.from_dict(log_dict)

        assert log.timestamp == timestamp
