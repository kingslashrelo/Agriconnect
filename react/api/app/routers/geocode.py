from fastapi import APIRouter, Query
import httpx

router = APIRouter()

@router.get("/search")
async def search(q: str = Query(...), limit: int = 8):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get("https://nominatim.openstreetmap.org/search", params={
            "q": q,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "countrycodes": "in"
        }, headers={"User-Agent": "AgriConnect/1.0"})
        return r.json()

@router.get("/reverse")
async def reverse(lat: float = Query(...), lon: float = Query(...)):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get("https://nominatim.openstreetmap.org/reverse", params={
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        }, headers={"User-Agent": "AgriConnect/1.0"})
        return r.json()
