from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import cache

router = APIRouter()

class ListingCreate(BaseModel):
    farmer_id: int
    crop_name: str
    quantity: float
    unit: str = "kg"
    price_per_unit: float
    harvest_date: str | None = None
    location: str | None = None
    description: str | None = None
    status: str = "active"

@router.get("")
@router.get("/")
def list_listings():
    cached = cache.get("listings:all")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("listings").select("*").order("listing_id", desc=True).execute()
    cache.put("listings:all", res.data, 30)
    return res.data

@router.get("/active")
def active_listings():
    cached = cache.get("listings:active")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        res = supabase.table("active_listings_view").select("*").execute()
    except Exception:
        res = supabase.table("listings").select("*").eq("status", "active").execute()
    cache.put("listings:active", res.data, 30)
    return res.data

@router.post("")
@router.post("/")
def create_listing(req: ListingCreate):
    from app.core.supabase import supabase
    data = req.model_dump()
    res = supabase.table("listings").insert(data).execute()
    if not res.data:
        raise HTTPException(400, "Failed to create listing")
    cache.clear("listings:", "marketplace:", "reports:")
    return res.data[0]

@router.get("/farmer/{farmer_id}")
def farmer_listings(farmer_id: int):
    key = f"listings:farmer:{farmer_id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("listings").select("*").eq("farmer_id", farmer_id).execute()
    cache.put(key, res.data, 30)
    return res.data
