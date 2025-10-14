# Trading Common

Async utilities shared across the trading platform for working with PostgreSQL inbox/outbox tables, Kafka producers/consumers, and schema validation via `trading-contracts`.

## Components
- `trading_common.db.DB` — connection pool with inbox/outbox bootstrap, idempotent helpers, and convenience wrappers for writing to the outbox.
- `trading_common.kafka.Producer` — resilient `aiokafka` producer prepared for SASL/SSL clusters and controlled retry behaviour.
- `trading_common.consumer_app.ConsumerApp` — batching Kafka consumer that wraps message handling in PostgreSQL transactions with inbox-based deduplication.
- `trading_common.outbox.OutboxProcessor` — helpers for reading, acknowledging, and vacuuming the outbox table.
- `trading_common.schema.ensure` — thin wrapper around `trading-contracts` JSON schema validation.
- `trading_common.settings_kafka` — baseline Kafka client settings hydrated from environment variables.

## Installation
```bash
# Inside a virtualenv; install runtime dependencies only
pip install -e .

# Install with development tooling (pytest, black, mypy, ...)
pip install -e ".[dev]"
```

## Configuration
### PostgreSQL
Provide a DSN string understood by `asyncpg`. The `DB.start()` method creates (or verifies) the `core.inbox` and `core.outbox` tables so that services can boot against an empty database.

```python
from trading_common.db import DB

db = DB("postgresql://postgres:postgres@127.0.0.1:55432/trading")
await db.start()
```

### Kafka
Baseline Kafka options come from `trading_common.settings_kafka`. They honour the following environment variables (defaults in parentheses):

| Variable | Purpose |
| --- | --- |
| `KAFKA_BOOTSTRAP_SERVERS` (`localhost:9092`) | Broker connection string |
| `KAFKA_SECURITY_PROTOCOL` (`SASL_SSL`) | `PLAINTEXT`, `SASL_SSL`, ... |
| `KAFKA_SASL_MECHANISM` (`PLAIN`) | Auth mechanism |
| `KAFKA_SASL_USERNAME` / `KAFKA_SASL_PASSWORD` (empty) | SASL credentials |
| `KAFKA_CLIENT_ID` (`market-data-service`) | Default client id |
| `KAFKA_ENABLE_IDEMPOTENCE` (`true`) | Producer idempotence flag |
| `KAFKA_LINGER_MS`, `KAFKA_BATCH_SIZE`, `KAFKA_COMPRESSION_TYPE`, ... | Producer tuning knobs |
| `KAFKA_ENABLE_AUTO_COMMIT` (`false`) | Consumer offset mode |
| `KAFKA_AUTO_OFFSET_RESET`, `KAFKA_MAX_POLL_INTERVAL_MS`, ... | Consumer runtime tuning |

Use `dict(...)` to clone and tweak the defaults before passing them into the Kafka helpers so that you do not mutate the shared module-level dictionaries:

```python
from trading_common import settings_kafka

producer = Producer(
    base_cfg={**settings_kafka.KAFKA_COMMON, "client_id": "strategy-service"},
    tuning=settings_kafka.PRODUCER_TUNING,
)
```

## Usage Examples
### Producer
```python
import asyncio
from trading_common import settings_kafka
from trading_common.kafka import Producer

async def publish() -> None:
    producer = Producer(
        base_cfg={**settings_kafka.KAFKA_COMMON, "client_id": "md-publisher"},
        tuning=settings_kafka.PRODUCER_TUNING,
    )
    await producer.start()
    try:
        await producer.send(
            topic="md.candles",
            key="BTCUSDT",
            payload={"event_id": "...", "open": 52000, "close": 52120},
        )
    finally:
        await producer.stop()

asyncio.run(publish())
```

### Consumer with Inbox/Outbox
```python
import asyncio
from trading_common import settings_kafka
from trading_common.consumer_app import ConsumerApp
from trading_common.db import DB
from trading_common.schema import ensure

async def handle(con, topic, key, payload):
    ensure("md.candle.closed@v1", payload)
    # Business logic ...

async def main() -> None:
    db = DB("postgresql://postgres:postgres@127.0.0.1:55432/trading")
    consumer = ConsumerApp(
        name="market-data-service",
        db=db,
        base_cfg={**settings_kafka.KAFKA_COMMON, "client_id": "market-data-service"},
        tuning=settings_kafka.CONSUMER_TUNING,
        topics=["md.candles"],
        group_id="md-service",
        handler=handle,
    )
    await consumer.start()
    try:
        await consumer.run()
    finally:
        await consumer.stop()

asyncio.run(main())
```

### Outbox Processing
```python
from trading_common.outbox import OutboxProcessor

processor = OutboxProcessor(db)
async with db.pool.acquire() as con:  # pool is available after db.start()
    events = await processor.get_pending_events(con, limit=100)
    for event_id, topic, key, payload in events:
        await producer.send(topic, key, payload)
        await processor.mark_published(con, event_id)
    await processor.cleanup_old_events(con, days_old=7)
```

## Development Workflow
```bash
pytest -m "not slow"       # Run fast tests
black src tests             # Format
isort src tests             # Import sorting
mypy src                    # Static typing
pytest --cov=trading_common --cov-report=term-missing
```

## Testing
- `pytest` — run the whole suite (asyncio tests use strict mode).
- `pytest -m "not slow"` — focus on the fast checks used in CI.
- `pytest --cov=trading_common --cov-report=term-missing` — optional coverage report.

These commands are mirrored in `.github/workflows/test.yml`, so keeping them green locally guarantees the CI job passes.

## Related Projects
- [`trading-contracts`](../contracts) — JSON schemas for every event type; install alongside this package to validate messages with `schema.ensure`.
- `infra/` in the monorepo provides Kafka/PostgreSQL containers for local development (`docker compose -f infra/docker-compose.yml up -d`).

## License
MIT License. See `LICENSE` for details.
