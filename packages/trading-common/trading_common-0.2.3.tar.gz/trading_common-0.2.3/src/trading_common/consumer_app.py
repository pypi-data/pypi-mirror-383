import asyncio
import json
from typing import Any, Awaitable, Callable, Dict, List, Optional

import asyncpg
from aiokafka import AIOKafkaConsumer

HandlerType = Callable[
    [asyncpg.Connection, str, Optional[str], Dict[str, Any]], Awaitable[None]
]


class ConsumerApp:
    def __init__(
        self,
        name: str,
        db: Any,  # твой обёрнутый пул asyncpg
        base_cfg: Dict[str, Any],  # settings_kafka.KAFKA_COMMON
        tuning: Dict[str, Any],  # settings_kafka.CONSUMER_TUNING
        topics: List[str],
        group_id: str,
        handler: HandlerType,
    ) -> None:
        self.name = name
        self.db = db
        self.cfg = {**base_cfg, **tuning, "group_id": group_id}
        self.topics = topics
        self.handler = handler
        self.c: Optional[AIOKafkaConsumer] = None

    async def start(self, retries: int = 20) -> None:
        await self.db.start()
        self.c = AIOKafkaConsumer(*self.topics, **self.cfg)
        delay = 1.0
        for _ in range(retries):
            try:
                await self.c.start()
                return
            except Exception:
                await asyncio.sleep(min(delay, 10.0))
                delay *= 1.5
        raise RuntimeError("Kafka consumer failed to start after retries")

    async def stop(self) -> None:
        if self.c:
            await self.c.stop()
            self.c = None
        await self.db.stop()

    async def run(self) -> None:
        assert self.c and self.db.pool
        while True:
            # забираем батчи со всех партиций
            batches: Dict[Any, List[Any]] = await self.c.getmany(
                timeout_ms=1000,
                max_records=self.cfg.get("max_poll_records", 1000),
            )
            if not batches:
                continue

            async with self.db.pool.acquire() as con:
                tx = con.transaction()
                await tx.start()
                try:
                    for tp, msgs in batches.items():
                        topic = tp.topic
                        for m in msgs:
                            payload = json.loads(m.value.decode())
                            key = m.key.decode() if m.key else None
                            # идемпотентность на уровне БД
                            msg_id = (
                                payload.get("event_id")
                                or f"{topic}:{m.partition}:{m.offset}"
                            )
                            if not await self.db.idempotent_begin(con, msg_id):
                                continue
                            await self.handler(con, topic, key, payload)
                            await self.db.idempotent_finish(con, msg_id)
                    await tx.commit()
                except Exception:
                    await tx.rollback()
                    # важно: не коммитим оффсеты → сообщения перечитаются
                    # (at-least-once)
                    raise
            # ручной коммит оффсетов только после успешной транзакции
            await self.c.commit()
