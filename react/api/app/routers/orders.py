from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import cache

router = APIRouter()

class OrderCreate(BaseModel):
    listing_id: int
    buyer_id: int
    quantity: float
    total_amount: float | None = None
    delivery_address: str | None = None
    notes: str | None = None

class StatusUpdate(BaseModel):
    order_id: int
    new_status: str
    changed_by: str | None = None

@router.get("")
@router.get("/")
def list_orders():
    cached = cache.get("orders:all")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    res = supabase.table("orders").select("*").order("order_id", desc=True).execute()
    cache.put("orders:all", res.data, 15)
    return res.data

@router.get("/history")
def order_history():
    cached = cache.get("orders:history")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        res = supabase.table("order_history_view").select("*").execute()
    except Exception:
        res = supabase.table("orders").select("*").order("order_date", desc=True).execute()
    cache.put("orders:history", res.data, 15)
    return res.data

@router.post("")
@router.post("/")
def create_order(req: OrderCreate):
    from app.core.supabase import supabase
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    data.setdefault("status", "pending")
    res = supabase.table("orders").insert(data).execute()
    if not res.data:
        raise HTTPException(400, "Failed to create order")
    cache.clear("orders:", "marketplace:", "reports:", "listings:")
    return res.data[0]

@router.post("/status")
def update_status(req: StatusUpdate):
    from app.core.supabase import supabase
    try:
        res = supabase.rpc("update_order_status", {
            "p_order_id": req.order_id,
            "p_new_status": req.new_status,
            "p_changed_by": req.changed_by
        }).execute()
        cache.clear("orders:", "reports:")
        return {"ok": True, "data": res.data}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/audit")
def order_audit():
    cached = cache.get("orders:audit")
    if cached is not None:
        return cached
    from app.core.supabase import supabase
    try:
        res = supabase.table("order_status_audit_view").select("*").execute()
    except Exception:
        res = supabase.table("order_status_history").select("*").order("changed_at", desc=True).execute()
    cache.put("orders:audit", res.data, 15)
    return res.data
