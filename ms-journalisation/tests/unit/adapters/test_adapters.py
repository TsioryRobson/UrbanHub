"""
Tests unitaires pour les adapters
"""
import pytest
from src.adapters.database.log_validator_adapter import LogValidator
from src.adapters.database.log_repository_adapter import InMemoryLogRepository, SQLiteLogRepository
from src.adapters.rabbitmq.log_consumer_adapter import MockLogConsumer
from src.adapters.api.log_api_adapter import LogApiAdapter
from src.domain.log import Log
from src.application.process_log_use_case import ProcessLogUseCase
from datetime import datetime
import os
import tempfile


class TestLogValidator:
    """Tests pour le validateur de logs"""

    @pytest.fixture
    def validator(self):
        """Création d'une instance du validateur"""
        return LogValidator()

    def test_validate_valid_log(self, validator):
        """Test la validation d'un log valide"""
        log_dict = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_service(self, validator):
        """Test la validation avec service manquant"""
        log_dict = {
            "event_type": "notification_sent",
            "message": "Email envoyé"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False
        assert any("service" in error.lower() for error in errors)

    def test_validate_missing_event_type(self, validator):
        """Test la validation avec event_type manquant"""
        log_dict = {
            "service": "MS Alerte",
            "message": "Email envoyé"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False

    def test_validate_missing_message(self, validator):
        """Test la validation avec message manquant"""
        log_dict = {
            "service": "MS Alerte",
            "event_type": "notification_sent"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False

    def test_validate_empty_service(self, validator):
        """Test la validation avec service vide"""
        log_dict = {
            "service": "",
            "event_type": "notification_sent",
            "message": "Email envoyé"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False
        assert any("empty" in error.lower() for error in errors)

    def test_validate_invalid_level(self, validator):
        """Test la validation avec un niveau invalide"""
        log_dict = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé",
            "level": "INVALID"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False
        assert any("level" in error.lower() for error in errors)

    def test_validate_valid_levels(self, validator):
        """Test la validation avec des niveaux valides"""
        valid_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]

        for level in valid_levels:
            log_dict = {
                "service": "MS Test",
                "event_type": "test",
                "message": "Test",
                "level": level
            }

            is_valid, errors = validator.validate(log_dict)
            assert is_valid is True

    def test_validate_invalid_timestamp_format(self, validator):
        """Test la validation avec un timestamp invalide"""
        log_dict = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé",
            "timestamp": "invalid-timestamp"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is False
        assert any("timestamp" in error.lower() for error in errors)

    def test_validate_valid_timestamp(self, validator):
        """Test la validation avec un timestamp valide"""
        log_dict = {
            "service": "MS Alerte",
            "event_type": "notification_sent",
            "message": "Email envoyé",
            "timestamp": "2026-04-21T10:00:00"
        }

        is_valid, errors = validator.validate(log_dict)

        assert is_valid is True


class TestInMemoryLogRepository:
    """Tests pour le repository en mémoire"""

    @pytest.fixture
    def repository(self):
        """Création d'une instance du repository"""
        return InMemoryLogRepository()

    def test_save_log(self, repository):
        """Test la sauvegarde d'un log"""
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé"
        )

        log_id = repository.save(log)

        assert log_id is not None
        assert log.log_id == log_id

    def test_find_by_id(self, repository):
        """Test la récupération d'un log par ID"""
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé"
        )

        log_id = repository.save(log)
        retrieved_log = repository.find_by_id(log_id)

        assert retrieved_log is not None
        assert retrieved_log.service == "MS Alerte"

    def test_find_by_id_nonexistent(self, repository):
        """Test la récupération avec un ID inexistant"""
        retrieved_log = repository.find_by_id("nonexistent")

        assert retrieved_log is None

    def test_find_by_service(self, repository):
        """Test la récupération par service"""
        log1 = Log(service="MS Alerte", event_type="event1", message="msg1")
        log2 = Log(service="MS Alerte", event_type="event2", message="msg2")
        log3 = Log(service="MS Analyse", event_type="event3", message="msg3")

        repository.save(log1)
        repository.save(log2)
        repository.save(log3)

        alerte_logs = repository.find_by_service("MS Alerte")

        assert len(alerte_logs) == 2
        assert all(log.service == "MS Alerte" for log in alerte_logs)

    def test_find_by_level(self, repository):
        """Test la récupération par niveau"""
        log1 = Log(service="MS Test", event_type="event1", message="msg1", level="INFO")
        log2 = Log(service="MS Test", event_type="event2", message="msg2", level="ERROR")
        log3 = Log(service="MS Test", event_type="event3", message="msg3", level="ERROR")

        repository.save(log1)
        repository.save(log2)
        repository.save(log3)

        error_logs = repository.find_by_level("ERROR")

        assert len(error_logs) == 2
        assert all(log.level == "ERROR" for log in error_logs)

    def test_find_all(self, repository):
        """Test la récupération de tous les logs"""
        log1 = Log(service="MS Test1", event_type="event1", message="msg1")
        log2 = Log(service="MS Test2", event_type="event2", message="msg2")
        log3 = Log(service="MS Test3", event_type="event3", message="msg3")

        repository.save(log1)
        repository.save(log2)
        repository.save(log3)

        all_logs = repository.find_all()

        assert len(all_logs) == 3

    def test_delete_by_id(self, repository):
        """Test la suppression d'un log"""
        log = Log(service="MS Test", event_type="event", message="msg")
        log_id = repository.save(log)

        deleted = repository.delete_by_id(log_id)

        assert deleted is True
        assert repository.find_by_id(log_id) is None

    def test_delete_by_id_nonexistent(self, repository):
        """Test la suppression avec un ID inexistant"""
        deleted = repository.delete_by_id("nonexistent")

        assert deleted is False


class TestSQLiteLogRepository:
    """Tests pour le repository SQLite"""

    @pytest.fixture
    def repository(self):
        """Création d'une instance du repository avec un fichier temporaire"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name

        repo = SQLiteLogRepository(db_path)
        yield repo

        # Nettoyage
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_save_and_retrieve_log(self, repository):
        """Test la sauvegarde et la récupération d'un log"""
        log = Log(
            service="MS Alerte",
            event_type="notification_sent",
            message="Email envoyé"
        )

        log_id = repository.save(log)
        retrieved_log = repository.find_by_id(log_id)

        assert retrieved_log is not None
        assert retrieved_log.service == "MS Alerte"
        assert retrieved_log.event_type == "notification_sent"

    def test_find_by_service_sqlite(self, repository):
        """Test la récupération par service avec SQLite"""
        log1 = Log(service="MS Alerte", event_type="event1", message="msg1")
        log2 = Log(service="MS Analyse", event_type="event2", message="msg2")

        repository.save(log1)
        repository.save(log2)

        alerte_logs = repository.find_by_service("MS Alerte")

        assert len(alerte_logs) == 1
        assert alerte_logs[0].service == "MS Alerte"


class TestMockLogConsumer:
    """Tests pour le mock consumer RabbitMQ"""

    def test_consumer_start_and_stop(self):
        """Test le démarrage et l'arrêt du consumer"""
        consumer = MockLogConsumer()

        assert consumer.is_connected() is False

        consumer.start(lambda msg: None)
        assert consumer.is_connected() is True

        consumer.stop()
        assert consumer.is_connected() is False

    def test_consumer_message_callback(self):
        """Test le callback des messages"""
        consumer = MockLogConsumer()
        received_messages = []

        def callback(msg):
            received_messages.append(msg)

        consumer.start(callback)
        consumer.publish_message("Test message 1")
        consumer.publish_message("Test message 2")

        assert len(received_messages) == 2
        assert received_messages[0] == "Test message 1"
        assert received_messages[1] == "Test message 2"


class TestLogApiAdapter:
    """Tests pour l'adaptateur API"""

    @pytest.fixture
    def setup(self):
        """Configuration initiale pour les tests"""
        repository = InMemoryLogRepository()
        validator = LogValidator()
        use_case = ProcessLogUseCase(repository, validator)
        api = LogApiAdapter(use_case)

        return api, use_case

    def test_get_all_logs(self, setup):
        """Test la récupération de tous les logs via l'API"""
        api, use_case = setup

        log_data = {
            "service": "MS Test",
            "event_type": "test",
            "message": "Test message"
        }
        use_case.execute(log_data)

        result = api.get_all_logs()

        assert result["status"] == "success"
        assert len(result["data"]) == 1
        assert result["data"][0]["service"] == "MS Test"

    def test_get_log_by_id(self, setup):
        """Test la récupération d'un log par ID via l'API"""
        api, use_case = setup

        log_data = {
            "service": "MS Test",
            "event_type": "test",
            "message": "Test message"
        }
        success, msg, log_id = use_case.execute(log_data)

        result = api.get_log_by_id(log_id)

        assert result["status"] == "success"
        assert result["data"]["id"] == log_id

    def test_get_log_by_nonexistent_id(self, setup):
        """Test la récupération d'un log inexistant via l'API"""
        api, use_case = setup

        result = api.get_log_by_id("nonexistent-id")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_get_logs_by_service(self, setup):
        """Test la récupération des logs par service via l'API"""
        api, use_case = setup

        log_data1 = {"service": "MS Alerte", "event_type": "event1", "message": "msg1"}
        log_data2 = {"service": "MS Analyse", "event_type": "event2", "message": "msg2"}

        use_case.execute(log_data1)
        use_case.execute(log_data2)

        result = api.get_logs_by_service("MS Alerte")

        assert result["status"] == "success"
        assert len(result["data"]) == 1
        assert result["data"][0]["service"] == "MS Alerte"

    def test_get_logs_by_level(self, setup):
        """Test la récupération des logs par niveau via l'API"""
        api, use_case = setup

        log_data1 = {"service": "MS Test", "event_type": "event1", "message": "msg1", "level": "INFO"}
        log_data2 = {"service": "MS Test", "event_type": "event2", "message": "msg2", "level": "ERROR"}

        use_case.execute(log_data1)
        use_case.execute(log_data2)

        result = api.get_logs_by_level("ERROR")

        assert result["status"] == "success"
        assert len(result["data"]) == 1
        assert result["data"][0]["level"] == "ERROR"

    def test_get_errors(self, setup):
        """Test la récupération des logs d'erreur via l'API"""
        api, use_case = setup

        log_data1 = {"service": "MS Test", "event_type": "event1", "message": "msg1", "level": "INFO"}
        log_data2 = {"service": "MS Test", "event_type": "event2", "message": "msg2", "level": "ERROR"}

        use_case.execute(log_data1)
        use_case.execute(log_data2)

        result = api.get_errors()

        assert result["status"] == "success"
        assert len(result["data"]) == 1
        assert result["data"][0]["level"] == "ERROR"

    def test_api_exception_handling(self, setup):
        """Test la gestion des exceptions dans l'API"""
        api, use_case = setup
        
        # Créer une exception en appelant une méthode avec une exception
        from unittest.mock import patch
        with patch.object(use_case, 'get_all_logs', side_effect=Exception("Database error")):
            result = api.get_all_logs()
            assert result["status"] == "error"
            assert "error" in result["message"].lower()

    def test_get_logs_by_service_empty(self, setup):
        """Test la récupération des logs par service vide"""
        api, use_case = setup

        result = api.get_logs_by_service("NonExistentService")

        assert result["status"] == "success"
        assert len(result["data"]) == 0

    def test_get_logs_by_level_empty(self, setup):
        """Test la récupération des logs par niveau vide"""
        api, use_case = setup

        result = api.get_logs_by_level("DEBUG")

        assert result["status"] == "success"
        assert len(result["data"]) == 0


class TestSQLiteRepository:
    """Additional tests pour SQLite repository"""

    @pytest.fixture
    def repository(self):
        """Création d'une instance du repository avec un fichier temporaire"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name

        repo = SQLiteLogRepository(db_path)
        yield repo

        # Nettoyage
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_sqlite_find_by_level(self, repository):
        """Test la récupération par niveau avec SQLite"""
        log1 = Log(service="MS Test", event_type="event1", message="msg1", level="INFO")
        log2 = Log(service="MS Test", event_type="event2", message="msg2", level="ERROR")

        repository.save(log1)
        repository.save(log2)

        error_logs = repository.find_by_level("ERROR")

        assert len(error_logs) == 1
        assert error_logs[0].level == "ERROR"

    def test_sqlite_find_all(self, repository):
        """Test la récupération de tous les logs avec SQLite"""
        log1 = Log(service="MS Test1", event_type="event1", message="msg1")
        log2 = Log(service="MS Test2", event_type="event2", message="msg2")

        repository.save(log1)
        repository.save(log2)

        all_logs = repository.find_all()

        assert len(all_logs) == 2

    def test_sqlite_find_by_nonexistent_service(self, repository):
        """Test la récupération d'un service inexistant"""
        log1 = Log(service="MS Test", event_type="event", message="msg")
        repository.save(log1)

        logs = repository.find_by_service("NonExistent")

        assert len(logs) == 0


class TestValidatorEdgeCases:
    """Tests pour les cas limites du validateur"""

    @pytest.fixture
    def validator(self):
        return LogValidator()

    def test_validate_empty_event_type(self, validator):
        """Test la validation avec event_type vide"""
        log_dict = {
            "service": "MS Test",
            "event_type": "",
            "message": "Test"
        }

        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

    def test_validate_empty_message(self, validator):
        """Test la validation avec message vide"""
        log_dict = {
            "service": "MS Test",
            "event_type": "test",
            "message": ""
        }

        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

    def test_validate_empty_level(self, validator):
        """Test la validation avec level vide"""
        log_dict = {
            "service": "MS Test",
            "event_type": "test",
            "message": "Test",
            "level": ""
        }

        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

    def test_validate_all_fields_valid(self, validator):
        """Test la validation avec tous les champs valides"""
        log_dict = {
            "service": "MS Test",
            "event_type": "test_event",
            "message": "Test message",
            "level": "WARNING",
            "timestamp": "2026-04-22T15:30:00",
            "metadata": {"key": "value"}
        }

        is_valid, errors = validator.validate(log_dict)
        assert is_valid is True


class TestMockConsumerEdgeCases:
    """Tests pour les cas limites du mock consumer"""

    def test_publish_without_start(self):
        """Test la publication sans démarrage"""
        consumer = MockLogConsumer()
        # Aucune exception attendue
        consumer.publish_message("Test message")

    def test_multiple_stop_calls(self):
        """Test les appels multiples de stop"""
        consumer = MockLogConsumer()
        consumer.start(lambda x: None)
        consumer.stop()
        consumer.stop()  # Double appel
        assert consumer.is_connected() is False
