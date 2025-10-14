from typing import Any, Dict, Optional

import ujson


def dumps(obj: Dict[str, Any]) -> bytes:
    # Ensure mypy sees a concrete str before encoding to bytes
    s: str = ujson.dumps(obj, ensure_ascii=False)
    return s.encode()


def encode_key(key: Optional[str]) -> Optional[bytes]:
    if key is None:
        return None
    return key.encode()
