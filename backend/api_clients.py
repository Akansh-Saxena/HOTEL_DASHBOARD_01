import os
import httpx
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace these later with your actual global API keys
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

class LiveDataEngine:
    def __init__(self):
        self.amadeus_token = None
        self.amadeus_base_url = "https://test.api.amadeus.com/v1" # Testing URL
        self.google_base_url = "https://maps.googleapis.com/maps/api/place"

    async def _get_amadeus_token(self):
        """Fetches the OAuth2 token required for Amadeus API endpoint requests."""
        if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
            logger.warning("Amadeus Keys missing. Generating Mock Token.")
            return "mock_token"
            
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": AMADEUS_API_KEY,
                "client_secret": AMADEUS_API_SECRET
            }
            try:
                response = await client.post(f"{self.amadeus_base_url}/security/oauth2/token", headers=headers, data=data)
                response.raise_for_status()
                token_data = response.json()
                self.amadeus_token = token_data.get("access_token")
            except Exception as e:
                logger.error(f"Failed to fetch Amadeus Token: {e}")

    async def fetch_hotel_prices(self, city_code: str, check_in: str, check_out: str):
        """Fetches live pricing and search data globally based on a city code."""
        if not self.amadeus_token:
            await self._get_amadeus_token()
            
        if self.amadeus_token == "mock_token":
             logger.info(f"Returning Mock Amadeus Data for {city_code}")
             return {
                 "data": [
                     {"hotel": {"name": f"Grand Oasis {city_code}"}, "offers": [{"price": {"total": "150.00", "currency": "USD"}}]},
                     {"hotel": {"name": f"City Hub {city_code}"}, "offers": [{"price": {"total": "80.00", "currency": "USD"}}]}
                 ]
             }

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.amadeus_token}"}
            params = {
                "cityCode": city_code,
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "roomQuantity": 1,
                "adults": 1,
            }
            try:
                response = await client.get(f"{self.amadeus_base_url}/reference-data/locations/hotels/by-city", headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Amadeus Hotel API Error: {e}")
                return None

    async def fetch_hotel_reviews(self, query: str):
        """Searches Google Places for the hotel to scrape user reviews."""
        if not GOOGLE_PLACES_API_KEY:
            logger.warning(f"Google API Key missing. Returning Mock Review Data for {query}")
            return [
                "The room was pristine and the staff was extremely helpful. 10/10.",
                "Terrible experience, the AC was broken and it was very loud at night."
            ]
            
        async with httpx.AsyncClient() as client:
            # First, find the Place ID
            search_params = {
                "query": query,
                "key": GOOGLE_PLACES_API_KEY
            }
            try:
                search_res = await client.get(f"{self.google_base_url}/textsearch/json", params=search_params)
                search_res.raise_for_status()
                search_data = search_res.json()
                
                if search_data.get("status") == "OK" and search_data.get("results"):
                    place_id = search_data["results"][0]["place_id"]
                    
                    # Next, fetch the detailed reviews using the Place ID
                    detail_params = {
                        "place_id": place_id,
                        "fields": "reviews",
                        "key": GOOGLE_PLACES_API_KEY
                    }
                    detail_res = await client.get(f"{self.google_base_url}/details/json", params=detail_params)
                    detail_res.raise_for_status()
                    detail_data = detail_res.json()
                    
                    if detail_data.get("status") == "OK" and "reviews" in detail_data.get("result", {}):
                         return [review["text"] for review in detail_data["result"]["reviews"]]
                return []
            except Exception as e:
                 logger.error(f"Google Places Review Extraction Error: {e}")
                 return []

# Example usage function for testing
async def run_test():
    engine = LiveDataEngine()
    print("Fetching Hotels for NYC...")
    hotels = await engine.fetch_hotel_prices("NYC", "2026-06-01", "2026-06-05")
    print(hotels)
    
    print("\nFetching Reviews for a specific hotel...")
    reviews = await engine.fetch_hotel_reviews("Grand Oasis NYC")
    print(reviews)

if __name__ == "__main__":
    asyncio.run(run_test())
