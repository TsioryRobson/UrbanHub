"""
Tests unitaires pour les ports
"""
import pytest
from uuid import uuid4
from src.ports.log_repository_port import LogRepositoryPort
from src.ports.log_consumer_port import LogConsumerPort
from src.ports.log_validator_port import LogValidatorPort
from src.domain.log import Log


class ConcreteLogRepository(LogRepositoryPort):
    """Implémentation concrète pour tester le port"""

    def __init__(self):
        self.logs = {}

    def save(self, log: Log) -> str:
        if not log.log_id:
            log.log_id = str(uuid4())
        self.logs[log.log_id] = log
        return log.log_id

    def find_by_id(self, log_id: str):
        return self.logs.get(log_id)

    def find_by_service(self, service: str):
        return [log for log in self.logs.values() if log.service == service]

    def find_by_level(self, level: str):
        return [log for log in self.logs.values() if str(log.level) == level]

    def find_all(self):
        return list(self.logs.values())

    def delete_by_id(self, log_id: str) -> bool:
        if log_id in self.logs:
            del self.logs[log_id]
            return True
        return False


class ConcreteLogConsumer(LogConsumerPort):
    """Implémentation concrète pour tester le port consumer"""

    def __init__(self):
        self._is_connected = False
        self._callback = None

    def start(self, callback):
        self._is_connected = True
        self._callback = callback

    def stop(self):
        self._is_connected = False

    def is_connected(self) -> bool:
        return self._is_connected


class ConcreteLogValidator(LogValidatorPort):
    """Implémentation concrète pour tester le port validator"""

    def validate(self, log_dict: dict) -> tuple[bool, list]:
        errors = []

        if "service" not in log_dict or not log_dict["service"]:
            errors.append("service is required")

        if "event_type" not in log_dict or not log_dict["event_type"]:
            errors.append("event_type is required")

        if "message" not in log_dict or not log_dict["message"]:
            errors.append("message is required")

        return len(errors) == 0, errors


class TestLogRepositoryPort:
    """Tests pour le port de repository"""

    @pytest.fixture
    def repository(self):
        return ConcreteLogRepository()

    def test_save_log(self, repository):
        """Test save method"""
        log = Log(service="MS Test", event_type="test", message="Test")
        log_id = repository.save(log)
        assert log_id is not None
        assert log_id == log.log_id

    def test_find_by_id(self, repository):
        """Test find_by_id method"""
        log = Log(service="MS Test", event_type="test", message="Test")
        repository.save(log)
        found = repository.find_by_id(log.log_id)
        assert found is not None
        assert found.service == "MS Test"

    def test_find_by_service(self, repository):
        """Test find_by_service method"""
        log1 = Log(service="MS Alerte", event_type="test", message="Test")
        log2 = Log(service="MS Alerte", event_type="test", message="Test")
        repository.save(log1)
        repository.save(log2)
        logs = repository.find_by_service("MS Alerte")
        assert len(logs) == 2

    def test_find_by_level(self, repository):
        """Test find_by_level method"""
        log1 = Log(service="MS Test", event_type="test", message="Test", level="INFO")
        log2 = Log(service="MS Test", event_type="test", message="Test", level="ERROR")
        repository.save(log1)
        repository.save(log2)
        info_logs = repository.find_by_level("INFO")
        assert len(info_logs) >= 1

    def test_find_all(self, repository):
        """Test find_all method"""
        log1 = Log(service="MS Test1", event_type="test", message="Test")
        log2 = Log(service="MS Test2", event_type="test", message="Test")
        repository.save(log1)
        repository.save(log2)
        all_logs = repository.find_all()
        assert len(all_logs) >= 2

    def test_delete_by_id(self, repository):
        """Test delete_by_id method"""
        log = Log(service="MS Test", event_type="test", message="Test")
        log_id = repository.save(log)
        deleted = repository.delete_by_id(log_id)
        assert deleted is True

    def test_find_by_service_empty(self, repository):
        """Test find_by_service when no logs exist"""
        logs = repository.find_by_service("NonExistent")
        assert len(logs) == 0

    def test_delete_nonexistent(self, repository):
        """Test delete_by_id with nonexistent ID"""
        deleted = repository.delete_by_id("nonexistent")
        assert deleted is False


class TestLogConsumerPort:
    """Tests pour le port de consumer"""

    @pytest.fixture
    def consumer(self):
        return ConcreteLogConsumer()

    def test_start_consumer(self, consumer):
        """Test start method"""
        consumer.start(lambda x: None)
        assert consumer.is_connected() is True

    def test_stop_consumer(self, consumer):
        """Test stop method"""
        consumer.start(lambda x: None)
        consumer.stop()
        assert consumer.is_connected() is False

    def test_is_connected_default(self, consumer):
        """Test is_connected before start"""
        assert consumer.is_connected() is False

    def test_callback_execution(self, consumer):
        """Test callback execution"""
        messages = []
        def callback(msg):
            messages.append(msg)
        
        consumer.start(callback)
        # Callback would be called when message is received
        assert consumer._callback is not None


class TestLogValidatorPort:
    """Tests pour le port de validator"""

    @pytest.fixture
    def validator(self):
        return ConcreteLogValidator()

    def test_validate_valid(self, validator):
        """Test validate with valid log"""
        log_dict = {
            "service": "MS Test",
            "event_type": "test",
            "message": "Test"
        }
        is_valid, errors = validator.validate(log_dict)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_service(self, validator):
        """Test validate missing service"""
        log_dict = {
            "event_type": "test",
            "message": "Test"
        }
        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_missing_event_type(self, validator):
        """Test validate missing event_type"""
        log_dict = {
            "service": "MS Test",
            "message": "Test"
        }
        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

    def test_validate_missing_message(self, validator):
        """Test validate missing message"""
        log_dict = {
            "service": "MS Test",
            "event_type": "test"
        }
        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

    def test_validate_empty_service(self, validator):
        """Test validate with empty service"""
        log_dict = {
            "service": "",
            "event_type": "test",
            "message": "Test"
        }
        is_valid, errors = validator.validate(log_dict)
        assert is_valid is False

