from fastapi import APIRouter
from app.core import cache

router = APIRouter()

@router.get("")
@router.get("/")
def list_buyers():
    cached = cache.get("buyers:all")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("buyers").select("*").order("buyer_id").execute()
    data = [{k: v for k, v in row.items() if k != "aadhaar_hash"} for row in res.data]
    cache.put("buyers:all", data, 30)
    return data

@router.get("/{buyer_id}")
def get_buyer(buyer_id: int):
    key = f"buyers:{buyer_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("buyers").select("*").eq("buyer_id", buyer_id).execute()
    data = {k: v for k, v in res.data[0].items() if k != "aadhaar_hash"} if res.data else {}
    cache.put(key, data, 30)
    return data
