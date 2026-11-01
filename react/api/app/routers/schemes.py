from fastapi import APIRouter
from app.core import cache

router = APIRouter()

@router.get("")
@router.get("/")
def list_schemes():
    cached = cache.get("schemes:all")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("schemes").select("*").order("scheme_id").execute().data
    except Exception:
        data = []
    cache.put("schemes:all", data, 60)
    return data

@router.get("/farmer/{farmer_id}")
def farmer_schemes(farmer_id: int):
    key = f"schemes:farmer:{farmer_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("schemes").select("*").eq("farmer_id", farmer_id).execute().data
    except Exception:
        data = []
    cache.put(key, data, 60)
    return data
