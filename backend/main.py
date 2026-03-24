import os
import httpx
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "booking-com.p.rapidapi.com"

@app.get("/api/v1/search-india")
async def search_all_india():
    """Pure India ka data fetch karne ka Dynamic Endpoint"""
    # India ki overall search ID (IATA/Dest ID for India Region)
    # Booking.com ID for India is 'in' or 'India'
    
    checkin = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    async with httpx.AsyncClient() as client:
        try:
            # Step 1: India region ke top hotels dhoondhna
            search_params = {
                "dest_id": "in", # 'in' is the country code for India in many travel APIs
                "dest_type": "country",
                "checkin_date": checkin,
                "checkout_date": checkout,
                "adults_number": "2",
                "order_by": "popularity",
                "filter_by_currency": "INR",
                "locale": "en-gb",
                "units": "metric"
            }

            response = await client.get(
                f"https://{RAPIDAPI_HOST}/v1/hotels/search",
                headers=headers,
                params=search_params,
                timeout=25.0
            )
            
            data = response.json()
            return {"source": "Global Neural Link", "results": data.get("result", [])}

        except Exception as e:
            return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "online", "key_active": bool(RAPIDAPI_KEY)}
