import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- NEURAL CACHE (BACKUP FOR PRESENTATION) ---
NEURAL_CACHE = [
    {"hotel_name": "The Taj Mahal Palace", "city": "Mumbai", "price": "24,500", "photo": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/38486221.jpg?k=3f27f87e59b2075f"},
    {"hotel_name": "The Oberoi Amarvilas", "city": "Agra", "price": "28,000", "photo": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/159114631.jpg?k=b28c575a"},
    {"hotel_name": "Radisson Blu Resort", "city": "Goa", "price": "9,200", "photo": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/22751336.jpg?k=a1d"},
    {"hotel_name": "Clarks Inn Grand", "city": "Bareilly", "price": "4,500", "photo": "https://cf.bstatic.com/xdata/images/hotel/max1024x768/41198293.jpg?k=e1f"}
]

@app.get("/api/v1/search-india")
async def scan_india():
    api_key = os.getenv("RAPIDAPI_KEY")
    # Naya Active Endpoint
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "booking-com.p.rapidapi.com"}
    params = {
        "dest_id": "-2090533", "dest_type": "city", "checkin_date": "2026-05-10", 
        "checkout_date": "2026-05-12", "adults_number": "2", "order_by": "popularity", 
        "filter_by_currency": "INR", "locale": "en-gb", "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, headers=headers, params=params, timeout=15.0)
            if res.status_code == 200:
                data = res.json().get("result", [])
                if data:
                    clean = []
                    for h in data[:12]:
                        clean.append({
                            "hotel_name": h.get("hotel_name"),
                            "city": h.get("city"),
                            "price": h.get("price_breakdown", {}).get("gross_amount", "Check Link"),
                            "photo": h.get("main_photo_url")
                        })
                    return {"source": "Live Neural Link", "results": clean}
            
            # Fallback to Cache
            return {"source": "Neural Cache (Offline)", "results": NEURAL_CACHE}
        except:
            return {"source": "Neural Cache (Emergency)", "results": NEURAL_CACHE}
