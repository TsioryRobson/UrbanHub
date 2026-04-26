"""
Tests unitaires pour le ProcessLogUseCase
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.application.process_log_use_case import ProcessLogUseCase
from src.domain.log import Log
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator


class TestProcessLogUseCase:
    """Tests pour le ProcessLogUseCase"""

    @pytest.fixture
    def setup(self):
        """Configuration initiale pour les tests"""
        self.repository = InMemoryLogRepository()
        self.validator = LogValidator()
        self.use_case = ProcessLogUseCase(self.repository, self.validator)

    def test_execute_valid_log(self, setup):
        """Test l'exécution avec un log valide"""
        log_data = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé avec succès",
            "level": "INFO"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is True
        assert "successfully" in message.lower()
        assert log_id != ""

    def test_execute_invalid_log_missing_service(self, setup):
        """Test l'exécution avec un log manquant le service"""
        log_data = {
            "event_type": "notification_sent",
            "message": "Email envoyé avec succès"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is False
        assert "validation" in message.lower()
        assert "service" in message.lower()
        assert log_id == ""

    def test_execute_invalid_log_missing_event_type(self, setup):
        """Test l'exécution avec un log manquant event_type"""
        log_data = {
            "service": "MS Alerte",
            "message": "Email envoyé avec succès"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is False
        assert log_id == ""

    def test_execute_invalid_log_missing_message(self, setup):
        """Test l'exécution avec un log manquant le message"""
        log_data = {
            "service": "MS Alerte",
            "event_type": "notification_sent"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is False
        assert log_id == ""

    def test_execute_invalid_log_empty_fields(self, setup):
        """Test l'exécution avec des champs vides"""
        log_data = {
            "service": "",
            "event_type": "",
            "message": ""
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is False
        assert log_id == ""

    def test_execute_invalid_log_level(self, setup):
        """Test l'exécution avec un niveau de log invalide"""
        log_data = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé",
            "level": "INVALID_LEVEL"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is False
        assert log_id == ""

    def test_execute_log_enrichment(self, setup):
        """Test l'enrichissement du log lors de l'exécution"""
        log_data = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé"
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is True
        log = self.repository.find_by_id(log_id)
        assert "service_source" in log.metadata
        assert log.metadata["service_source"] == "MS Alerte"
        assert "context" in log.metadata

    def test_execute_multiple_logs(self, setup):
        """Test l'exécution de plusieurs logs"""
        logs_data = [
            {
                "service": "MS Alerte",
                "event_type": "notification_sent",
                "message": "Email envoyé"
            },
            {
                "service": "MS Analyse",
                "event_type": "analysis_completed",
                "message": "Analyse complétée"
            },
            {
                "service": "MS Collecte",
                "event_type": "error_occurred",
                "message": "Erreur lors de la collecte",
                "level": "ERROR"
            }
        ]

        log_ids = []
        for log_data in logs_data:
            success, message, log_id = self.use_case.execute(log_data)
            assert success is True
            log_ids.append(log_id)

        assert len(log_ids) == 3
        assert len(set(log_ids)) == 3  # Tous les IDs sont uniques

    def test_get_log_by_id(self, setup):
        """Test la récupération d'un log par son ID"""
        log_data = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé"
        }

        success, message, log_id = self.use_case.execute(log_data)
        retrieved_log = self.use_case.get_log_by_id(log_id)

        assert retrieved_log is not None
        assert retrieved_log.log_id == log_id
        assert retrieved_log.service == "MS Alerte"

    def test_get_log_by_nonexistent_id(self, setup):
        """Test la récupération d'un log avec un ID inexistant"""
        retrieved_log = self.use_case.get_log_by_id("nonexistent-id")

        assert retrieved_log is None

    def test_get_logs_by_service(self, setup):
        """Test la récupération des logs par service"""
        logs_data = [
            {"service": "MS Alerte", "event_type": "event1", "message": "msg1"},
            {"service": "MS Alerte", "event_type": "event2", "message": "msg2"},
            {"service": "MS Analyse", "event_type": "event3", "message": "msg3"}
        ]

        for log_data in logs_data:
            self.use_case.execute(log_data)

        alerte_logs = self.use_case.get_logs_by_service("MS Alerte")
        analyse_logs = self.use_case.get_logs_by_service("MS Analyse")

        assert len(alerte_logs) == 2
        assert len(analyse_logs) == 1

    def test_get_logs_by_level(self, setup):
        """Test la récupération des logs par niveau"""
        logs_data = [
            {"service": "MS Test", "event_type": "event1", "message": "msg1", "level": "INFO"},
            {"service": "MS Test", "event_type": "event2", "message": "msg2", "level": "ERROR"},
            {"service": "MS Test", "event_type": "event3", "message": "msg3", "level": "ERROR"}
        ]

        for log_data in logs_data:
            self.use_case.execute(log_data)

        info_logs = self.use_case.get_logs_by_level("INFO")
        error_logs = self.use_case.get_logs_by_level("ERROR")

        assert len(info_logs) == 1
        assert len(error_logs) == 2

    def test_get_all_logs(self, setup):
        """Test la récupération de tous les logs"""
        logs_data = [
            {"service": "MS Alerte", "event_type": "event1", "message": "msg1"},
            {"service": "MS Analyse", "event_type": "event2", "message": "msg2"},
            {"service": "MS Collecte", "event_type": "event3", "message": "msg3"}
        ]

        for log_data in logs_data:
            self.use_case.execute(log_data)

        all_logs = self.use_case.get_all_logs()

        assert len(all_logs) == 3

    def test_execute_with_custom_timestamp(self, setup):
        """Test l'exécution avec un timestamp personnalisé"""
        timestamp = "2026-04-21T10:00:00"
        log_data = {
            "service": "MS Test",
            "event_type": "test_event",
            "message": "Test message",
            "timestamp": timestamp
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is True
        log = self.repository.find_by_id(log_id)
        assert log.timestamp.isoformat() == timestamp

    def test_execute_with_metadata(self, setup):
        """Test l'exécution avec des métadonnées"""
        log_data = {
            "service": "MS Test",
            "event_type": "test_event",
            "message": "Test message",
            "metadata": {"user_id": "123", "request_id": "456"}
        }

        success, message, log_id = self.use_case.execute(log_data)

        assert success is True
        log = self.repository.find_by_id(log_id)
        assert log.metadata["user_id"] == "123"
        assert log.metadata["request_id"] == "456"

    def test_execute_exception_handling(self, setup):
        """Test la gestion des exceptions"""
        # Mock le repository pour lever une exception
        mock_repository = Mock()
        mock_repository.save.side_effect = Exception("Database error")

        use_case = ProcessLogUseCase(mock_repository, self.validator)

        log_data = {
            "service": "MS Test",
            "event_type": "test_event",
            "message": "Test message"
        }

        success, message, log_id = use_case.execute(log_data)

        assert success is False
        assert "error" in message.lower()
        assert log_id == ""
