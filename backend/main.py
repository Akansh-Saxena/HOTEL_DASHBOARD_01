import os
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# --- AUTHOR: AKANSH SAXENA ---
# --- MODULE: AETHER CORE ENGINE (BACKEND) ---

app = FastAPI(title="Aether Core Engine", version="1.0.0")

# --- CORS SETUP ---
# Isse Vercel/Streamlit ko access milega
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, replace "*" with your specific Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "saxenaakansh29@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password")

# --- MODELS ---
class SendOTPRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

# --- ROUTES ---
@app.get("/health")
async def health_check():
    """Neural Handshake Endpoint"""
    return {"status": "online", "system": "Aether Core", "owner": "Akansh Saxena"}

@app.post("/api/auth/send-otp")
async def generate_and_send_otp(req: SendOTPRequest):
    new_otp = str(random.randint(100000, 999999))
    # Yahan aapka email sending logic aayega
    return {"status": "success", "message": f"OTP generated for {req.email}"}

@app.post("/api/auth/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    if len(req.otp) == 6:
        return {"access_token": "neural_token_123", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid OTP")
