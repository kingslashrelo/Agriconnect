from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import cache

router = APIRouter()

class LoginRequest(BaseModel):
    aadhaar: str
    role: str | None = None  # 'farmer' or 'buyer' or None for auto-detect

class RegisterRequest(BaseModel):
    role: str
    aadhaar: str
    name: str
    phone: str | None = None
    village: str | None = None
    district: str | None = None
    state: str | None = None
    land_size_acres: float | None = None
    crop_preference: str | None = None
    business_name: str | None = None
    buyer_type: str | None = None

@router.post("/login")
def login(req: LoginRequest):
    from app.core.supabase import supabase
    aadhaar = (req.aadhaar or "").strip()
    if not (aadhaar.isdigit() and len(aadhaar) == 12):
        raise HTTPException(400, "Enter a valid 12-digit Aadhaar number")
    if req.role and req.role not in ("farmer", "buyer"):
        raise HTTPException(400, "Invalid role")
    roles = ["farmer", "buyer"] if not req.role else [req.role]
    for role in roles:
        fn = "aadhaar_farmer_login" if role == "farmer" else "aadhaar_buyer_login"
        rows = supabase.rpc(fn, {"p_aadhaar": aadhaar}).execute().data or []
        if rows:
            return {"role": role, "user": rows[0]}
    raise HTTPException(404, "No account matches that Aadhaar")

@router.post("/register")
def register(req: RegisterRequest):
    from app.core.supabase import supabase
    aadhaar = (req.aadhaar or "").strip()
    if not (aadhaar.isdigit() and len(aadhaar) == 12):
        raise HTTPException(400, "Enter a valid 12-digit Aadhaar number")
    if not (req.name or "").strip():
        raise HTTPException(400, "Name is required")
    if req.role == "farmer":
        data = {
            "name": req.name.strip(),
            "village": (req.village or "").strip() or None,
            "contact": (req.phone or "").strip() or None,
            "primary_crop": (req.crop_preference or "").strip() or None,
        }
        if not data["village"]:
            raise HTTPException(400, "Village / area is required")
        try:
            res = supabase.table("farmers").insert(data).execute()
            if not res.data:
                raise HTTPException(400, "Failed to create farmer")
            fid = res.data[0]["farmer_id"]
            supabase.rpc("set_farmer_aadhaar", {"p_farmer_id": fid, "p_aadhaar": aadhaar}).execute()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"Could not register: {e}")
        user = {k: v for k, v in res.data[0].items() if k != "aadhaar_hash"}
        cache.clear("marketplace:", "farmers:")
        return {"role": "farmer", "user": user}
    elif req.role == "buyer":
        data = {
            "name": req.name.strip(),
            "contact": (req.phone or "").strip() or None,
            "buyer_type": (req.buyer_type or "retailer").strip().lower(),
            "location": (req.village or "").strip() or None,
        }
        if not data["location"]:
            raise HTTPException(400, "Location is required")
        try:
            res = supabase.table("buyers").insert(data).execute()
            if not res.data:
                raise HTTPException(400, "Failed to create buyer")
            bid = res.data[0]["buyer_id"]
            supabase.rpc("set_buyer_aadhaar", {"p_buyer_id": bid, "p_aadhaar": aadhaar}).execute()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"Could not register: {e}")
        user = {k: v for k, v in res.data[0].items() if k != "aadhaar_hash"}
        cache.clear("marketplace:", "buyers:")
        return {"role": "buyer", "user": user}
    raise HTTPException(400, "Invalid role")
