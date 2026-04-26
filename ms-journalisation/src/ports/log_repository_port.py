"""
Port de sortie : LogRepositoryPort
Interface pour la persistance des logs
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.log import Log


class LogRepositoryPort(ABC):
    """Interface pour la sauvegarde et récupération des logs"""

    @abstractmethod
    def save(self, log: Log) -> str:
        """
        Sauvegarde un log en base de données

        Args:
            log: L'objet Log à sauvegarder

        Returns:
            L'identifiant du log sauvegardé
        """
        pass

    @abstractmethod
    def find_by_id(self, log_id: str) -> Optional[Log]:
        """
        Récupère un log par son identifiant

        Args:
            log_id: Identifiant du log

        Returns:
            L'objet Log ou None si non trouvé
        """
        pass

    @abstractmethod
    def find_by_service(self, service: str) -> List[Log]:
        """
        Récupère tous les logs d'un service

        Args:
            service: Nom du service

        Returns:
            Liste des logs du service
        """
        pass

    @abstractmethod
    def find_by_level(self, level: str) -> List[Log]:
        """
        Récupère tous les logs d'un niveau spécifique

        Args:
            level: Niveau de log (INFO, ERROR, etc.)

        Returns:
            Liste des logs du niveau spécifié
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Log]:
        """
        Récupère tous les logs

        Returns:
            Liste de tous les logs
        """
        pass

    @abstractmethod
    def delete_by_id(self, log_id: str) -> bool:
        """
        Supprime un log par son identifiant

        Args:
            log_id: Identifiant du log

        Returns:
            True si suppression réussie, False sinon
        """
        pass
