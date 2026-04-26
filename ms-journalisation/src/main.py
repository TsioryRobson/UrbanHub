"""
Point d'entrée du microservice Journalisation
"""
import json
import os
from src.application.process_log_use_case import ProcessLogUseCase
from src.adapters.database.log_repository_adapter import InMemoryLogRepository
from src.adapters.database.log_validator_adapter import LogValidator
from src.adapters.rabbitmq.log_consumer_adapter import RabbitMQLogConsumer


def main():
    """Point d'entrée principal du microservice"""

    # Initialisation des adapters
    log_repository = InMemoryLogRepository()
    log_validator = LogValidator()

    # Initialisation du use case
    process_log_use_case = ProcessLogUseCase(log_repository, log_validator)

    # Initialisation du consumer RabbitMQ
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
    log_consumer = RabbitMQLogConsumer(host=rabbitmq_host)

    def handle_message(message: str) -> None:
        """Traite un message reçu de RabbitMQ"""
        try:
            log_data = json.loads(message)
            success, msg, log_id = process_log_use_case.execute(log_data)
            if success:
                print(f"✓ Log processed: {log_id}")
            else:
                print(f"✗ Error: {msg}")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON: {e}")
        except Exception as e:
            print(f"✗ Error processing message: {e}")

    # Démarrage du consumer
    print("Starting Log Microservice...")
    log_consumer.start(handle_message)


if __name__ == "__main__":
    main()
