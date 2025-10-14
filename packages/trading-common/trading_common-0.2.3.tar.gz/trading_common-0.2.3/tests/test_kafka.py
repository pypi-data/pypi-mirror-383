import json
import ssl
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from trading_common.consumer_app import ConsumerApp
from trading_common.kafka import Producer, dumps


def test_dumps() -> None:
    """Test JSON serialization"""
    data = {"key": "value", "number": 42}
    result = dumps(data)
    assert isinstance(result, bytes)
    assert json.loads(result.decode()) == data


@pytest.mark.asyncio
async def test_producer_start_stop() -> None:
    """Test producer start and stop"""
    producer = Producer(
        base_cfg={"bootstrap_servers": "localhost:9092"},
        tuning={"linger_ms": 0},
    )

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    with patch("trading_common.kafka.AIOKafkaProducer", return_value=mock_producer):
        producer.p = mock_producer

        # Test stop
        await producer.stop()
        mock_producer.stop.assert_called_once()


@pytest.mark.asyncio
async def test_producer_send() -> None:
    """Test producer send with key"""
    producer = Producer(
        base_cfg={"bootstrap_servers": "localhost:9092"},
        tuning={"linger_ms": 0},
    )

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    producer.p = mock_producer

    topic = "test.topic"
    key = "test-key"
    payload = {"data": "test-value"}

    await producer.send(topic, key, payload)

    mock_producer.send_and_wait.assert_called_with(
        topic, key=key.encode(), value=dumps(payload)
    )


@pytest.mark.asyncio
async def test_producer_send_no_key() -> None:
    """Test producer send without key"""
    producer = Producer(
        base_cfg={"bootstrap_servers": "localhost:9092"},
        tuning={"linger_ms": 0},
    )

    # Mock AIOKafkaProducer
    mock_producer = AsyncMock()
    producer.p = mock_producer

    topic = "test.topic"
    payload = {"data": "test-value"}

    await producer.send(topic, None, payload)

    mock_producer.send_and_wait.assert_called_with(
        topic, key=None, value=dumps(payload)
    )


@pytest.mark.asyncio
async def test_consumer_app_start_stop() -> None:
    """Test consumer app start and stop"""
    # Mock DB
    mock_db = MagicMock()
    mock_db.start = AsyncMock()
    mock_db.stop = AsyncMock()

    # Mock AIOKafkaConsumer
    mock_consumer = AsyncMock()
    with patch(
        "trading_common.consumer_app.AIOKafkaConsumer", return_value=mock_consumer
    ):
        consumer_app = ConsumerApp(
            "test-consumer",
            mock_db,
            base_cfg={"bootstrap_servers": "localhost:9092"},
            tuning={"enable_auto_commit": False},
            topics=["test.topic"],
            group_id="test-group",
            handler=AsyncMock(),
        )

        consumer_app.c = mock_consumer

        # Test stop
        await consumer_app.stop()
        mock_consumer.stop.assert_called_once()
        mock_db.stop.assert_called_once()


@pytest.mark.asyncio
async def test_consumer_app_run_batch_processing() -> None:
    """Test consumer app batch processing setup"""
    # Mock DB
    mock_db = MagicMock()
    mock_db.start = AsyncMock()
    mock_db.stop = AsyncMock()
    mock_pool = MagicMock()
    mock_db.pool = mock_pool

    # Mock connection
    mock_connection = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    # Mock transaction
    mock_transaction = AsyncMock()
    mock_connection.transaction.return_value = mock_transaction

    # Mock consumer
    mock_consumer = AsyncMock()
    mock_consumer.getmany.return_value = {}
    mock_consumer.commit = AsyncMock()

    # Mock handler
    mock_handler = AsyncMock()

    consumer_app = ConsumerApp(
        name="test-consumer",
        db=mock_db,
        base_cfg={"bootstrap_servers": "localhost:9092"},
        tuning={"enable_auto_commit": False},
        topics=["test.topic"],
        group_id="test-group",
        handler=mock_handler,
    )

    consumer_app.c = mock_consumer

    # Test that the setup is correct without running the infinite loop
    assert consumer_app.c is not None
    assert consumer_app.db.pool is not None
    assert consumer_app.handler is not None

    # Verify consumer was initialized
    mock_consumer.getmany.assert_not_called()  # Should not be called yet


def test_producer_hydrates_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "env-broker:9092")
    monkeypatch.setenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
    monkeypatch.setenv("KAFKA_SASL_MECHANISM", "PLAIN")
    monkeypatch.setenv("KAFKA_SASL_USERNAME", "env-user")
    monkeypatch.setenv("KAFKA_SASL_PASSWORD", "env-pass")
    monkeypatch.setenv("KAFKA_CLIENT_ID", "env-client")

    producer = Producer(base_cfg={}, tuning={})

    assert producer.cfg["bootstrap_servers"] == "env-broker:9092"
    assert producer.cfg["security_protocol"] == "SASL_SSL"
    assert producer.cfg["sasl_mechanism"] == "PLAIN"
    assert producer.cfg["sasl_plain_username"] == "env-user"
    assert producer.cfg["sasl_plain_password"] == "env-pass"
    assert producer.cfg["client_id"] == "env-client"


def test_producer_ensures_ssl_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")
    monkeypatch.setenv("KAFKA_SSL_CAFILE", "/tmp/ca.pem")
    monkeypatch.setenv("KAFKA_SSL_VERIFY", "false")
    monkeypatch.setenv("KAFKA_SSL_CHECK_HOSTNAME", "false")

    dummy_ctx = SimpleNamespace(check_hostname=True, verify_mode=ssl.CERT_REQUIRED)

    with patch(
        "trading_common.kafka.ssl.create_default_context", return_value=dummy_ctx
    ) as create_ctx:
        producer = Producer(base_cfg={}, tuning={})

    create_ctx.assert_called_once_with(cafile="/tmp/ca.pem")
    assert producer.cfg["ssl_context"] is dummy_ctx
    assert dummy_ctx.check_hostname is False
    assert dummy_ctx.verify_mode == ssl.CERT_NONE


def test_producer_keeps_existing_ssl_context(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_SECURITY_PROTOCOL", "SASL_SSL")

    custom_ctx = object()
    with patch("trading_common.kafka.ssl.create_default_context") as create_ctx:
        producer = Producer(base_cfg={"ssl_context": custom_ctx}, tuning={})

    create_ctx.assert_not_called()
    assert producer.cfg["ssl_context"] is custom_ctx
