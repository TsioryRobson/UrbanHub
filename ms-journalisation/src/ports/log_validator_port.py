"""
Port de validation : LogValidatorPort
Interface pour la validation des logs
"""
from abc import ABC, abstractmethod
from typing import List


class LogValidatorPort(ABC):
    """Interface pour la validation des logs"""

    @abstractmethod
    def validate(self, log_dict: dict) -> tuple[bool, List[str]]:
        """
        Valide un log

        Args:
            log_dict: Dictionnaire représentant un log

        Returns:
            Tuple (is_valid, list_of_errors)
        """
        pass
