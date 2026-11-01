from fastapi import APIRouter, Query
import httpx

router = APIRouter()

@router.get("/forecast")
async def forecast(lat: float = Query(...), lon: float = Query(...)):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        return r.json()
