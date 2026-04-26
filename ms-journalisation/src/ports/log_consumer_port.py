"""
Port d'entrée : LogConsumerPort
Interface pour la consommation des logs depuis RabbitMQ
"""
from abc import ABC, abstractmethod
from typing import Callable


class LogConsumerPort(ABC):
    """Interface pour la consommation des logs depuis RabbitMQ"""

    @abstractmethod
    def start(self, callback: Callable[[str], None]) -> None:
        """
        Démarre la consommation des messages

        Args:
            callback: Fonction de rappel appelée pour chaque message reçu
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Arrête la consommation des messages"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Vérifie si le consumer est connecté

        Returns:
            True si connecté, False sinon
        """
        pass
