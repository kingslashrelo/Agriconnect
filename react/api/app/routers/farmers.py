from fastapi import APIRouter
from app.core import cache

router = APIRouter()

@router.get("")
@router.get("/")
def list_farmers():
    cached = cache.get("farmers:all")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("farmers").select("*").order("farmer_id").execute()
    data = [{k: v for k, v in row.items() if k != "aadhaar_hash"} for row in res.data]
    cache.put("farmers:all", data, 30)
    return data

@router.get("/{farmer_id}")
def get_farmer(farmer_id: int):
    key = f"farmers:{farmer_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("farmers").select("*").eq("farmer_id", farmer_id).execute()
    data = {k: v for k, v in res.data[0].items() if k != "aadhaar_hash"} if res.data else {}
    cache.put(key, data, 30)
    return data
