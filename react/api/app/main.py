from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.routers import auth, farmers, buyers, listings, orders, reports, crop_advisor, schemes, weather, geocode, marketplace

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["farmers"])
app.include_router(buyers.router, prefix="/api/buyers", tags=["buyers"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(crop_advisor.router, prefix="/api/crop-advisor", tags=["crop-advisor"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["schemes"])
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(geocode.router, prefix="/api/geocode", tags=["geocode"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/health")
def health():
    return {"status": "ok"}
