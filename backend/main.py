from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import logging

from backend.api_clients import LiveDataEngine
from backend.nlp_pipeline import NLPReviewBrain
# from backend.database import get_db, init_db # For later caching use

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aether Hospitality Global API",
    description="High-Speed Backend for Live Hotel Data & NLP Sentiment",
    version="1.0.0"
)

# Global singleton instances for our engines to reuse connections
data_engine = LiveDataEngine()
nlp_brain = NLPReviewBrain()

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up Aether Backend...")
    # await init_db() # Initialize PostgreSQL tables if they don't exist

class SearchRequest(BaseModel):
    city_code: str
    check_in: str
    check_out: str

@app.post("/api/hotels")
async def search_hotels(req: SearchRequest):
    """
    Phase 1: Fetch live hotel pricing from Amadeus.
    TODO: Add PostgreSQL Cache hit check before fetching.
    """
    logger.info(f"Searching hotels globally for: {req.city_code}")
    results = await data_engine.fetch_hotel_prices(req.city_code, req.check_in, req.check_out)
    
    if not results:
        raise HTTPException(status_code=500, detail="Failed to fetch live hotel data")
    
    # Optional: Save results to database cache here
    
    return {"status": "success", "city": req.city_code, "hotels": results.get("data", [])}

class ReviewRequest(BaseModel):
    hotel_name: str

@app.post("/api/reviews")
async def analyze_hotel_reviews(req: ReviewRequest):
    """
    Phase 2: Fetch raw reviews from Google Places and process them through the NLP brain.
    """
    logger.info(f"Fetching reviews for {req.hotel_name}")
    raw_reviews = await data_engine.fetch_hotel_reviews(req.hotel_name)
    
    if not raw_reviews:
         return {"status": "success", "message": "No reviews found or API key missing.", "nlp_analysis": None}
         
    logger.info("Routing reviews to NLP Pipeline...")
    nlp_results = await nlp_brain.process_reviews(raw_reviews)
    
    return {"status": "success", "hotel": req.hotel_name, "nlp_analysis": nlp_results}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Aether Backend API"}
