import time
from threading import Lock

_store: dict[str, tuple[float, object]] = {}
_lock = Lock()


def get(key: str):
    with _lock:
        item = _store.get(key)
        if item is None:
            return None
        expires, value = item
        if expires <= time.monotonic():
            del _store[key]
            return None
        return value


def put(key: str, value: object, ttl: float) -> None:
    with _lock:
        _store[key] = (time.monotonic() + ttl, value)


def clear(*prefixes: str) -> None:
    with _lock:
        if not prefixes:
            _store.clear()
            return
        for key in list(_store):
            if key.startswith(prefixes):
                del _store[key]
