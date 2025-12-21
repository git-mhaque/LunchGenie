"""
Review fetching and enrichment logic for LunchGenie.
Handles review retrieval from API results, including Yelp review detail, with fallback as needed.
"""

import requests

YELP_BUSINESS_DETAIL_URL = "https://api.yelp.com/v3/businesses/{id}/reviews"

class ReviewFetcher:
    def __init__(self, config):
        self.config = config

    def get_reviews(self, entry):
        """
        Returns a list of reviews for a restaurant entry, using provider reviews if available,
        or fetching from Yelp API as fallback if configured.
        """
        provider = getattr(self.config, "restaurant_provider", None)
        reviews = []
        if "reviews" in entry and entry["reviews"]:
            reviews = entry["reviews"]
        elif provider == "yelp":
            # Fetch reviews via Yelp API
            try:
                detail_url = YELP_BUSINESS_DETAIL_URL.format(id=entry["id"])
                headers = {"Authorization": f"Bearer {self.config.yelp_api_key}"}
                resp = requests.get(detail_url, headers=headers, timeout=7)
                resp.raise_for_status()
                reviews = [r["text"] for r in resp.json().get("reviews", [])]
            except Exception:
                reviews = []
        # Could add more provider-specific logic if desired
        return reviews
