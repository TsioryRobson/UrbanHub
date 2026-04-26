"""
Use Case : ProcessLogUseCase
Orchestration du traitement des logs
"""
from typing import Dict, Any, List
from src.domain.log import Log
from src.ports.log_repository_port import LogRepositoryPort
from src.ports.log_validator_port import LogValidatorPort


class ProcessLogUseCase:
    """Use case pour traiter et sauvegarder les logs"""

    def __init__(
        self,
        log_repository: LogRepositoryPort,
        log_validator: LogValidatorPort
    ):
        """
        Initialise le use case

        Args:
            log_repository: Port de persistance des logs
            log_validator: Port de validation des logs
        """
        self.log_repository = log_repository
        self.log_validator = log_validator

    def execute(self, log_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Exécute le traitement d'un log

        Étapes:
        1. Validation
        2. Transformation en objet métier Log
        3. Enrichissement (optionnel)
        4. Sauvegarde

        Args:
            log_data: Dictionnaire contenant les données du log

        Returns:
            Tuple (success, message, log_id)
        """
        # Étape 1: Validation
        is_valid, errors = self.log_validator.validate(log_data)
        if not is_valid:
            error_msg = f"Validation failed: {', '.join(errors)}"
            return False, error_msg, ""

        try:
            # Étape 2: Transformation
            log = Log.from_dict(log_data)

            # Étape 3: Enrichissement
            log = self._enrich_log(log)

            # Étape 4: Sauvegarde
            log_id = self.log_repository.save(log)

            return True, "Log processed and saved successfully", log_id

        except Exception as e:
            return False, f"Error processing log: {str(e)}", ""

    def _enrich_log(self, log: Log) -> Log:
        """
        Enrichit le log avec des métadonnées additionnelles

        Args:
            log: Le log à enrichir

        Returns:
            Le log enrichi
        """
        # Normalisation du service
        log.metadata["service_source"] = log.service

        # Ajout du contexte
        if "context" not in log.metadata:
            log.metadata["context"] = "system"

        return log

    def get_log_by_id(self, log_id: str) -> Log:
        """
        Récupère un log par son identifiant

        Args:
            log_id: Identifiant du log

        Returns:
            L'objet Log
        """
        return self.log_repository.find_by_id(log_id)

    def get_logs_by_service(self, service: str) -> List[Log]:
        """
        Récupère tous les logs d'un service

        Args:
            service: Nom du service

        Returns:
            Liste des logs
        """
        return self.log_repository.find_by_service(service)

    def get_logs_by_level(self, level: str) -> List[Log]:
        """
        Récupère tous les logs d'un niveau spécifique

        Args:
            level: Niveau de log

        Returns:
            Liste des logs
        """
        return self.log_repository.find_by_level(level)

    def get_all_logs(self) -> List[Log]:
        """
        Récupère tous les logs

        Returns:
            Liste de tous les logs
        """
        return self.log_repository.find_all()
