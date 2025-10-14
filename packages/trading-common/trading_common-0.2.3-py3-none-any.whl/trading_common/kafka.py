import asyncio
import importlib
import importlib.util
import os
import ssl
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer

from .kafka_common import dumps, encode_key


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


class Producer:
    def __init__(self, base_cfg: Dict[str, Any], tuning: Dict[str, Any]) -> None:
        """
        base_cfg: settings_kafka.KAFKA_COMMON
        tuning:   settings_kafka.PRODUCER_TUNING
        """
        # aiokafka ожидает плоские kwargs
        self.cfg = {**base_cfg, **tuning}
        self._hydrate_from_env()
        self._ensure_ssl_context()
        self.p: Optional[AIOKafkaProducer] = None

    async def start(self, retries: int = 20) -> None:
        # «мягкие» ретраи, чтобы деплой не падал, если брокер прогревается
        delay = 1.0
        last_error: Exception | None = None

        # Если продюсер уже стартовал – сначала остановим его, чтобы не держать ресурс
        if self.p is not None:
            await self.stop()

        for attempt in range(retries):
            producer = AIOKafkaProducer(**self.cfg)
            try:
                await producer.start()
            except Exception as exc:  # pragma: no cover - зависит от внешнего брокера
                last_error = exc
                try:
                    await producer.stop()
                except Exception:
                    pass  # pragma: no cover - best effort cleanup

                await asyncio.sleep(min(delay, 10.0))
                delay *= 1.5
                continue

            self.p = producer
            return

        error = RuntimeError("Kafka producer failed to start after retries")
        if last_error is not None:
            raise error from last_error
        raise error

    async def stop(self) -> None:
        if self.p:
            await self.p.stop()
            self.p = None

    async def send(
        self, topic: str, key: Optional[str], payload: Dict[str, Any]
    ) -> None:
        assert self.p is not None, "Producer not started"
        await self.p.send_and_wait(topic, key=encode_key(key), value=dumps(payload))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_ssl_context(self) -> None:
        protocol = str(self.cfg.get("security_protocol", "")).upper()
        if protocol not in {"SSL", "SASL_SSL"}:
            return
        if self.cfg.get("ssl_context") is not None:
            return

        cafile = os.getenv("KAFKA_SSL_CAFILE")
        context: ssl.SSLContext
        try:
            if cafile:
                context = ssl.create_default_context(cafile=cafile)
            else:
                certifi_cafile = _certifi_cafile()
                if certifi_cafile:
                    context = ssl.create_default_context(cafile=certifi_cafile)
                else:
                    context = ssl.create_default_context()
        except Exception:
            context = ssl.create_default_context()

        if not _env_bool("KAFKA_SSL_VERIFY", True):
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        if not _env_bool("KAFKA_SSL_CHECK_HOSTNAME", True):
            context.check_hostname = False

        self.cfg["ssl_context"] = context

    def _hydrate_from_env(self) -> None:
        overrides = {
            "bootstrap_servers": "KAFKA_BOOTSTRAP_SERVERS",
            "security_protocol": "KAFKA_SECURITY_PROTOCOL",
            "sasl_mechanism": "KAFKA_SASL_MECHANISM",
            "sasl_plain_username": "KAFKA_SASL_USERNAME",
            "sasl_plain_password": "KAFKA_SASL_PASSWORD",
            "client_id": "KAFKA_CLIENT_ID",
        }
        for key, env_name in overrides.items():
            current = self.cfg.get(key)
            if current:
                continue
            env_value = os.getenv(env_name)
            if env_value:
                self.cfg[key] = env_value


def _certifi_cafile() -> Optional[str]:
    spec = importlib.util.find_spec("certifi")
    if spec is None:
        return None

    try:
        certifi = importlib.import_module("certifi")
    except Exception:  # pragma: no cover - import can still fail at runtime
        return None

    where = getattr(certifi, "where", None)
    if not callable(where):
        return None

    cafile = where()
    if isinstance(cafile, str):
        return cafile
    return None
