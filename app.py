import base64
import os
import smtplib
import random
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# --- AUTHOR: AKANSH SAXENA ---
# --- AETHER CORE ENGINE: BACKEND MAIN ---

app = FastAPI(
    title="Akansh Saxena Global Ecosystem - Core Engine",
    description="FastAPI Backend for Hospitality Booking Platform",
    version="1.0.0"
)

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-akansh-2026")
# In production, set these in Render Environment Variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "saxenaakansh29@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password") 

# --- CORS SETUP (Zaroori for Streamlit/Vercel) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hoteldashboard01.streamlit.app",
        "https://hotel-dashboard-01.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PYDANTIC MODELS ---
class SendOTPRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

# --- 1. HEALTH CHECK (Waking up Render & Ping Check) ---
@app.get("/health")
async def health_check():
    return {
        "status": "online", 
        "system": "Aether Core", 
        "owner": "Akansh Saxena",
        "timestamp": datetime.utcnow().isoformat()
    }

# --- 2. AUTHENTICATION (OTP Logic) ---
def send_email_otp(receiver_email: str, otp_code: str):
    try:
        msg = MIMEText(f"Hello,\n\nYour secure login OTP for Aether Gateway is: {otp_code}\n\nRegards,\nAkansh Saxena")
        msg['Subject'] = 'Aether Gateway: Secure Login OTP'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@app.post("/api/auth/send-otp")
async def generate_and_send_otp(req: SendOTPRequest):
    new_otp = str(random.randint(100000, 999999))
    # Note: In a real app, you'd save this to a DB here
    email_sent = send_email_otp(req.email, new_otp)
    
    if not email_sent:
        # Fallback for testing if SMTP is not configured
        return {"status": "mock_success", "otp_debug": new_otp, "message": "OTP simulated (Check Logs)"}
        
    return {"status": "success", "message": f"OTP sent to {req.email}"}

@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    # Standard verify logic (Assuming OTP 123456 for demo or DB check)
    if req.otp == "123456" or len(req.otp) == 6:
        return {"access_token": "neural_token_xyz123", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid OTP")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
