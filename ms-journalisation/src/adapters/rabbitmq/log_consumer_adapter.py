"""
Adapter RabbitMQ : LogConsumerAdapter
Consommation des logs depuis RabbitMQ
"""
from typing import Callable, Optional
import json
from src.ports.log_consumer_port import LogConsumerPort


class RabbitMQLogConsumer(LogConsumerPort):
    """Consommateur de logs depuis RabbitMQ"""

    def __init__(
        self,
        host: str = "localhost",
        queue_name: str = "logs_queue",
        port: int = 5672
    ):
        """
        Initialise le consumer RabbitMQ

        Args:
            host: Hôte de RabbitMQ
            queue_name: Nom de la queue
            port: Port de RabbitMQ
        """
        self.host = host
        self.queue_name = queue_name
        self.port = port
        self.connection: Optional[object] = None
        self.channel: Optional[object] = None
        self._is_connected = False

    def start(self, callback: Callable[[str], None]) -> None:
        """
        Démarre la consommation des messages

        Args:
            callback: Fonction de rappel appelée pour chaque message reçu
        """
        try:
            import pika

            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self._is_connected = True

            self.channel.queue_declare(queue=self.queue_name, durable=True)

            def message_callback(ch, method, properties, body):
                try:
                    message = body.decode('utf-8')
                    callback(message)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=message_callback
            )

            print(f"Started consuming from {self.queue_name}")
            self.channel.start_consuming()

        except Exception as e:
            print(f"Error starting consumer: {e}")
            self._is_connected = False
            raise

    def stop(self) -> None:
        """Arrête la consommation des messages"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        self._is_connected = False

    def is_connected(self) -> bool:
        """Vérifie si le consumer est connecté"""
        return self._is_connected
