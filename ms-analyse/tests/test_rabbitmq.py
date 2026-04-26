import json
from typing import Any
from unittest.mock import Mock, patch

from pika.exceptions import AMQPConnectionError

from src.adapters.rabbitmq.consumer import RabbitMQConsumer
from src.adapters.rabbitmq.publisher import RabbitMQPublisher


def build_analysis_result(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {"outputs": outputs}


def test_consumer_callback_builds_domain_payload() -> None:
    use_case = Mock()
    consumer = RabbitMQConsumer(use_case)

    consumer.callback(
        None,
        None,
        None,
        json.dumps(
            {
                "sensorId": "sensor-1",
                "zoneId": "zone-A",
                "windowStart": "2026-04-11T10:00:00Z",
                "windowEnd": "2026-04-11T10:00:15Z",
                "vehicles": [{"speedKmh": 45, "vehicleType": "car"}],
                "vehicleCount": 1,
            }
        ).encode(),
    )

    payload = use_case.execute.call_args.args[0]

    assert payload.sensor_id == "sensor-1"
    assert payload.zone_id == "zone-A"
    assert payload.vehicles[0].speed_kmh == 45
    assert payload.vehicle_count == 1


@patch("src.adapters.rabbitmq.consumer.pika.BlockingConnection", side_effect=AMQPConnectionError("down"))
def test_consumer_start_consuming_handles_connection_error(_: Mock, capsys) -> None:
    consumer = RabbitMQConsumer(Mock())

    consumer.start_consuming()

    assert "RabbitMQ indisponible" in capsys.readouterr().out


def test_consumer_start_consuming_declares_and_consumes_queue() -> None:
    consumer = RabbitMQConsumer(Mock())
    channel = Mock()
    connection = Mock()
    connection.channel.return_value = channel

    with patch("src.adapters.rabbitmq.consumer.pika.BlockingConnection", return_value=connection):
        consumer.start_consuming()

    channel.queue_declare.assert_called_once_with(queue="collecte_queue")
    channel.basic_consume.assert_called_once()
    channel.start_consuming.assert_called_once()


@patch("src.adapters.rabbitmq.publisher.pika.BlockingConnection", side_effect=AMQPConnectionError("down"))
def test_publisher_handles_connection_error(_: Mock, capsys) -> None:
    publisher = RabbitMQPublisher()
    analysis_result = build_analysis_result([])

    publisher.publish(analysis_result)

    assert "Impossible de publier les sorties d'analyse." in capsys.readouterr().out


def test_publisher_only_publishes_allowed_channels() -> None:
    publisher = RabbitMQPublisher()
    channel = Mock()
    connection = Mock()
    connection.channel.return_value = channel

    analysis_result = build_analysis_result(
        [
            {"channel": "alert_queue", "payload": {"a": 1}},
            {"channel": "analysis.user.notification", "payload": {"b": 2}},
            {"channel": "postgresql.analysis_results", "payload": {"c": 3}},
        ]
    )

    with patch("src.adapters.rabbitmq.publisher.pika.BlockingConnection", return_value=connection):
        publisher.publish(analysis_result)

    assert channel.queue_declare.call_count == 2
    assert channel.basic_publish.call_count == 2
    connection.close.assert_called_once()
