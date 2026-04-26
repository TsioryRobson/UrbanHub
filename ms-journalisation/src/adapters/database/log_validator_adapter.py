"""
Adapter de validation : LogValidatorAdapter
Validation des logs
"""
from typing import List
from src.ports.log_validator_port import LogValidatorPort


class LogValidator(LogValidatorPort):
    """Validateur de logs"""

    def __init__(self):
        """Initialise le validateur"""
        self.required_fields = ["service", "event_type", "message"]

    def validate(self, log_dict: dict) -> tuple[bool, List[str]]:
        """
        Valide un log

        Args:
            log_dict: Dictionnaire représentant un log

        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []

        # Vérifier les champs obligatoires
        for field in self.required_fields:
            if field not in log_dict or not log_dict[field]:
                errors.append(f"Missing required field: {field}")

        # Vérifier que les champs ne sont pas vides
        for field in self.required_fields:
            if field in log_dict and isinstance(log_dict[field], str):
                if len(log_dict[field].strip()) == 0:
                    errors.append(f"Field {field} cannot be empty")

        # Vérifier le niveau de log
        if "level" in log_dict:
            valid_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
            if log_dict["level"] not in valid_levels:
                errors.append(f"Invalid log level: {log_dict['level']}")

        # Vérifier le timestamp
        if "timestamp" in log_dict:
            from datetime import datetime
            if isinstance(log_dict["timestamp"], str):
                try:
                    datetime.fromisoformat(log_dict["timestamp"])
                except ValueError:
                    errors.append(f"Invalid timestamp format: {log_dict['timestamp']}")

        return len(errors) == 0, errors
