from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from fastapi import APIRouter
from app.core import cache

router = APIRouter()
_pool = ThreadPoolExecutor(max_workers=4)
_stats_lock = Lock()
_EMPTY = {"listings": 0, "orders": 0, "farmers": 0, "buyers": 0}

@router.get("/stats")
def stats():
    cached = cache.get("marketplace:stats")
    if cached is not None:
        return cached
    with _stats_lock:
        cached = cache.get("marketplace:stats")
        if cached is not None:
            return cached
        from app.core.supabase import supabase
        try:
            _ = supabase.postgrest
            def count(table: str, column: str) -> int:
                return supabase.table(table).select(column, count="exact").execute().count or 0
            futures = [
                _pool.submit(count, "listings", "listing_id"),
                _pool.submit(count, "orders", "order_id"),
                _pool.submit(count, "farmers", "farmer_id"),
                _pool.submit(count, "buyers", "buyer_id"),
            ]
            payload = {
                "listings": futures[0].result(),
                "orders": futures[1].result(),
                "farmers": futures[2].result(),
                "buyers": futures[3].result(),
            }
            cache.put("marketplace:stats", payload, 300)
            return payload
        except Exception:
            return _EMPTY
