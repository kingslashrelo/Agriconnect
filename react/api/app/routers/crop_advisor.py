from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RecommendRequest(BaseModel):
    ph: float = 6.5
    moisture: float = 50
    n: float = 3.0
    p: float = 3.0
    k: float = 3.0
    temp: float = 28
    season: str = "Kharif"

@router.post("/recommend")
def recommend(req: RecommendRequest):
    from app.core.supabase import supabase
    try:
        res = supabase.rpc("recommend_crops", {
            "p_ph": req.ph,
            "p_moisture": req.moisture,
            "p_n": req.n,
            "p_p": req.p,
            "p_k": req.k,
            "p_temp": req.temp,
            "p_season": req.season,
        }).execute()
        return res.data
    except Exception as e:
        return {"error": str(e)}

@router.get("/crops")
def crops():
    from app.core.supabase import supabase
    try:
        res = supabase.table("crop_recommendations").select("*").execute()
        return res.data
    except Exception:
        return []
