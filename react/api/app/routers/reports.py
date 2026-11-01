from fastapi import APIRouter
from app.core import cache

router = APIRouter()

@router.get("/most-active-buyers")
def most_active_buyers():
    key = "reports:buyers"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("most_active_buyers_view").select("*").execute().data
    except Exception:
        try:
            data = supabase.rpc("get_most_active_buyers").execute().data
        except Exception:
            data = []
    cache.put(key, data, 30)
    return data

@router.get("/farmer-ratings")
def farmer_ratings():
    key = "reports:ratings"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.rpc("get_farmer_ratings").execute().data
    except Exception:
        try:
            data = supabase.table("farmer_avg_rating_view").select("*").execute().data
        except Exception:
            data = []
    cache.put(key, data, 30)
    return data

@router.get("/inventory")
def inventory():
    key = "reports:inventory"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("inventory_view").select("*").execute().data
    except Exception:
        data = []
    cache.put(key, data, 30)
    return data

@router.get("/low-stock")
def low_stock():
    key = "reports:low-stock"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("low_stock_view").select("*").execute().data
    except Exception:
        data = []
    cache.put(key, data, 30)
    return data

@router.get("/monthly-sales")
def monthly_sales():
    key = "reports:monthly-sales"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.table("monthly_sales_summary_view").select("*").execute().data
    except Exception:
        data = []
    cache.put(key, data, 30)
    return data

@router.get("/farmer-revenue/{farmer_id}")
def farmer_revenue(farmer_id: int):
    key = f"reports:revenue:{farmer_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        data = supabase.rpc("get_farmer_revenue", {"p_farmer_id": farmer_id}).execute().data
    except Exception:
        data = []
    cache.put(key, data, 30)
    return data
