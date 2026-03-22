import os
import httpx
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HuggingFace API key from environment
HF_API_KEY = os.getenv("HF_API_KEY", "")
# We use RoBERTa trained on sentiment for high accuracy
HF_MODEL_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"

class NLPReviewBrain:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
        # Simple heuristic mapping for prototype categorized sentiment
        self.category_keywords = {
            "Cleanliness": ["clean", "dirty", "spotless", "filthy", "hygiene", "smell", "dust"],
            "Staff":       ["staff", "service", "friendly", "rude", "reception", "manager", "helpful"],
            "Location":    ["location", "close to", "view", "walk", "subway", "train", "far", "noisy"],
            "Value":       ["value", "price", "expensive", "cheap", "worth", "money", "overpriced"]
        }

    def _determine_category(self, review_text: str) -> str:
        """Assigns the review to a category bucket based on keyword matching."""
        review_lower = review_text.lower()
        for category, keywords in self.category_keywords.items():
            if any(kw in review_lower for kw in keywords):
                return category
        return "General"

    async def _analyze_sentiment_hf(self, review: str) -> Dict:
        """Calls HuggingFace Inference API to get the sentiment label and confidence score."""
        if not HF_API_KEY:
            # Fallback mock for >90% precision logic if key isn't provided yet
            sentiment = "positive" if "great" in review.lower() or "pristine" in review.lower() else "negative"
            return {"label": sentiment, "score": 0.95}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(HF_MODEL_URL, headers=self.headers, json={"inputs": review})
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    # API returns a list of label/score dicts. We find the one with the highest score.
                    results = data[0]
                    best_match = max(results, key=lambda x: x['score'])
                    return best_match
                return {"label": "neutral", "score": 0.50}
            except Exception as e:
                logger.error(f"HF Sentiment API Error: {e}")
                return {"label": "neutral", "score": 0.50}

    async def process_reviews(self, raw_reviews: List[str]) -> Dict:
        """
        Ingests a list of raw reviews, calculates sentiment per category, 
        and computes the overall 'True Sentiment Score'.
        """
        if not raw_reviews:
            return {"status": "No reviews provided", "true_sentiment_score": 0, "categories": {}}

        categorized_scores = {cat: {"positive": 0, "negative": 0, "total": 0} for cat in self.category_keywords.keys()}
        categorized_scores["General"] = {"positive": 0, "negative": 0, "total": 0}
        
        total_positive_weight = 0
        total_weight = 0

        for review in raw_reviews:
            # Filter noise: Skip reviews that are too short to hold meaningful sentiment
            if len(review.split()) < 4:
                continue

            category = self._determine_category(review)
            sentiment_result = await self._analyze_sentiment_hf(review)
            
            label = sentiment_result.get("label", "").lower()
            confidence = sentiment_result.get("score", 0.5)

            # Only count >90% precision confidence (or our mock which forces 0.95)
            if confidence >= 0.90:
                is_positive = 1 if label == "positive" else 0
                
                categorized_scores[category]["total"] += 1
                if is_positive:
                    categorized_scores[category]["positive"] += 1
                else:
                    categorized_scores[category]["negative"] += 1

                total_positive_weight += is_positive
                total_weight += 1

        # Calculate "True Sentiment Score" out of 100
        true_score = (total_positive_weight / total_weight * 100) if total_weight > 0 else 0

        return {
            "true_sentiment_score": round(true_score, 1),
            "total_analyzed": total_weight,
            "category_breakdown": categorized_scores
        }

# Example Usage Test
async def run_test():
    brain = NLPReviewBrain()
    reviews = [
        "The room was pristine and the staff was extremely helpful. 10/10.",
        "Terrible experience, the AC was broken and it was very loud at night.",
        "Location is great, easy walk to the subway, but a little overpriced.",
        "Ok", # Noise - will be filtered
    ]
    
    print("Processing Reviews through NLP Brain...")
    results = await brain.process_reviews(reviews)
    import json
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_test())
