# Quick Start Guide

A minimal walk-through for installing `trading-common`, running the local dependencies, and wiring a service that reads and writes Kafka events backed by PostgreSQL.

## 1. Start Local Infra
From the monorepo root run:

```bash
docker compose -f infra/docker-compose.yml up -d
```

This brings up:
- PostgreSQL on `127.0.0.1:55432`
- Redpanda (Kafka-compatible) on `127.0.0.1:9092`
- Redpanda Console on `http://localhost:8080`

## 2. Install the Package
Create a virtual environment for the service and install `trading-common` in editable mode with development tooling:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "trading-common-py[dev]"
```

To install runtime dependencies only:

```bash
pip install -e trading-common-py
```

## 3. Connect to PostgreSQL
Use `trading_common.db.DB` to open a connection pool. The first call to `start()` ensures the inbox/outbox tables exist.

```python
import asyncio
from trading_common.db import DB

async def bootstrap_db() -> DB:
    db = DB("postgresql://postgres:postgres@127.0.0.1:55432/trading")
    await db.start()
    return db

asyncio.run(bootstrap_db())
```

## 4. Publish Events
Configure the Kafka producer using the defaults provided by `trading_common.settings_kafka` and publish an event.

```python
import asyncio
from trading_common import settings_kafka
from trading_common.kafka import Producer

async def publish_example() -> None:
    producer = Producer(
        base_cfg={**settings_kafka.KAFKA_COMMON, "client_id": "example-publisher"},
        tuning=settings_kafka.PRODUCER_TUNING,
    )
    await producer.start()
    try:
        await producer.send(
            topic="md.ticker@v1",
            key="BTCUSDT",
            payload={"event_id": "...", "price": 50123.45},
        )
    finally:
        await producer.stop()

asyncio.run(publish_example())
```

## 5. Consume Events with Idempotency
Wrap your handler in `ConsumerApp`. Each batch is processed inside a PostgreSQL transaction and deduplicated via the inbox table.

```python
import asyncio
from trading_common import settings_kafka
from trading_common.consumer_app import ConsumerApp
from trading_common.db import DB
from trading_common.schema import ensure

async def handle_event(con, topic, key, payload):
    ensure("md.ticker@v1", payload)  # Validate schema
    # business logic here

async def main() -> None:
    db = DB("postgresql://postgres:postgres@127.0.0.1:55432/trading")
    consumer = ConsumerApp(
        name="ticker-consumer",
        db=db,
        base_cfg={**settings_kafka.KAFKA_COMMON, "client_id": "ticker-consumer"},
        tuning=settings_kafka.CONSUMER_TUNING,
        topics=["md.ticker"],
        group_id="ticker-service",
        handler=handle_event,
    )
    await consumer.start()
    try:
        await consumer.run()
    finally:
        await consumer.stop()

asyncio.run(main())
```

## 6. Process the Outbox
Use the outbox helpers to publish stored events and clean up published rows.

```python
from trading_common.outbox import OutboxProcessor

processor = OutboxProcessor(db)
async with db.pool.acquire() as con:  # make sure db.start() was called
    events = await processor.get_pending_events(con, limit=100)
    for event_id, topic, key, payload in events:
        await producer.send(topic, key, payload)
        await processor.mark_published(con, event_id)
    await processor.cleanup_old_events(con, days_old=14)
```

## 7. Run Tests and Tooling
Execute the built-in test suite and quality checks before committing:

```bash
cd trading-common-py
pytest -m "not slow"
black src tests
isort src tests
mypy src
```

The full `pytest` run should pass without failures; make sure to fix or update tests if you extend the library.

## 8. Tear Down Infra
After you are done experimenting:

```bash
docker compose -f infra/docker-compose.yml down
```

You are now ready to plug these primitives into the service you are building.
