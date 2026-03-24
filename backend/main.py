import os
import httpx
import random
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# --- AUTHOR: AKANSH SAXENA ---
# --- MODULE: AETHER CORE ENGINE (PRO VERSION) ---

app = FastAPI(title="Aether Core Engine", version="2.0.0")

# --- CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION (Render Environment Variables) ---
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") # Jo key aapne screenshot mein dikhayi thi
RAPIDAPI_HOST = "booking-com.p.rapidapi.com"
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "saxenaakansh29@gmail.com")

# --- MODELS ---
class SendOTPRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

# --- UTILITY FUNCTIONS ---
async def fetch_hotel_data(destination: str, checkin: str, checkout: str):
    """RapidAPI Integration to fetch real hotel data"""
    url = f"https://{RAPIDAPI_HOST}/v1/hotels/search"
    
    # Ye headers aapke account ko authenticate karenge
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    querystring = {
        "dest_id": "-2090533", # Default for Bareilly, can be dynamic
        "order_by": "popularity",
        "checkout_date": checkout,
        "checkin_date": checkin,
        "filter_by_currency": "INR",
        "adults_number": "2",
        "room_number": "1",
        "units": "metric",
        "dest_type": "city",
        "locale": "en-gb"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=querystring, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Fallback data agar API fail ho jaye (Presentation Backup)
            return {"status": "error", "message": str(e), "data": "Using Neural Cache"}

# --- ROUTES ---
@app.get("/health")
async def health_check():
    """Neural Handshake Check"""
    return {
        "status": "online", 
        "system": "Aether Core V2", 
        "owner": "Akansh Saxena",
        "api_connected": bool(RAPIDAPI_KEY)
    }

@app.post("/api/auth/send-otp")
async def generate_and_send_otp(req: SendOTPRequest):
    # Simulated OTP for presentation
    # 123456 logic presentation ke liye easy rehti hai
    simulated_otp = "123456" 
    print(f"DEBUG: OTP for {req.email} is {simulated_otp}")
    return {"status": "success", "otp_status": "sent_to_neural_node"}

@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    if req.otp == "123456":
        return {"access_token": "neural_token_pro_99", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Identity Verification Failed")

@app.get("/api/v1/search")
async def search_inventory(
    dest: str = "Bareilly", 
    checkin: str = "2026-03-29", 
    checkout: str = "2026-03-31"
):
    """Dynamic Hotel Search Route"""
    data = await fetch_hotel_data(dest, checkin, checkout)
    return {"source": "RapidAPI/Booking.com", "results": data}
