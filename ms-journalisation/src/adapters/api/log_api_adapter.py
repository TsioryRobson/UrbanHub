"""
Adapter API REST : LogApiAdapter
Interface REST pour consulter les logs
"""
from typing import Dict, Any
from src.application.process_log_use_case import ProcessLogUseCase


class LogApiAdapter:
    """Adaptateur API REST pour les logs"""

    def __init__(self, process_log_use_case: ProcessLogUseCase):
        """
        Initialise l'adaptateur API

        Args:
            process_log_use_case: Use case de traitement des logs
        """
        self.use_case = process_log_use_case

    def get_all_logs(self) -> Dict[str, Any]:
        """
        Récupère tous les logs

        Returns:
            Dictionnaire avec la liste des logs
        """
        try:
            logs = self.use_case.get_all_logs()
            return {
                "status": "success",
                "data": [log.to_dict() for log in logs]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_log_by_id(self, log_id: str) -> Dict[str, Any]:
        """
        Récupère un log par son identifiant

        Args:
            log_id: Identifiant du log

        Returns:
            Dictionnaire avec le log
        """
        try:
            log = self.use_case.get_log_by_id(log_id)
            if not log:
                return {
                    "status": "error",
                    "message": f"Log with id {log_id} not found"
                }
            return {
                "status": "success",
                "data": log.to_dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_logs_by_service(self, service: str) -> Dict[str, Any]:
        """
        Récupère les logs d'un service

        Args:
            service: Nom du service

        Returns:
            Dictionnaire avec la liste des logs
        """
        try:
            logs = self.use_case.get_logs_by_service(service)
            return {
                "status": "success",
                "data": [log.to_dict() for log in logs]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_logs_by_level(self, level: str) -> Dict[str, Any]:
        """
        Récupère les logs d'un niveau spécifique

        Args:
            level: Niveau de log

        Returns:
            Dictionnaire avec la liste des logs
        """
        try:
            logs = self.use_case.get_logs_by_level(level)
            return {
                "status": "success",
                "data": [log.to_dict() for log in logs]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_errors(self) -> Dict[str, Any]:
        """
        Récupère tous les logs d'erreur

        Returns:
            Dictionnaire avec la liste des erreurs
        """
        return self.get_logs_by_level("ERROR")
