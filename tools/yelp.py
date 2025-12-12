"""
YelpPlugin: Fetch restaurants from Yelp Fusion API, filter with supplied criteria.
"""

from typing import List, Dict, Any, Optional
import requests

from lunchgenie.config import Config
from tools.base import PluginBase, PluginError

YELP_API_URL = "https://api.yelp.com/v3/businesses/search"

class YelpPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "yelp"

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        if not self.config.yelp_api_key:
            raise PluginError("Missing Yelp API key in config/environment.")
        self.api_key = self.config.yelp_api_key

    def search_restaurants(
        self, 
        query: str, 
        location: str = '', 
        criteria: Dict[str, Any] = None,
        latitude: float = None,
        longitude: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search restaurants on Yelp. If latitude and longitude are provided, they override location.
        """
        criteria = criteria or {}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "term": query or "restaurants",
            "categories": criteria.get("categories", ""),  # e.g. "indian,malaysian,chinese"
            "radius": criteria.get("radius", 1200),        # meters; default ~15-min walk
            "sort_by": "rating",
            "limit": 10
        }
        if latitude is not None and longitude is not None:
            params["latitude"] = latitude
            params["longitude"] = longitude
        else:
            params["location"] = location or "Melbourne"
        # Yelp's best rating filter done post-query since the API does not filter by rating directly
        min_rating = criteria.get("min_rating", 0)

        try:
            resp = requests.get(YELP_API_URL, headers=headers, params=params, timeout=8)
            resp.raise_for_status()
            businesses = resp.json().get("businesses", [])
        except Exception as e:
            raise PluginError(f"Yelp API request failed: {e}")
        results = []
        for b in businesses:
            if b.get('rating', 0) >= min_rating:
                results.append({
                    "name": b.get("name"),
                    "address": " ".join(b.get("location", {}).get("display_address", [])),
                    "rating": b.get("rating"),
                    "review_count": b.get("review_count"),
                    "categories": [cat["title"] for cat in b.get("categories", [])],
                    "url": b.get("url"),
                    "distance_m": int(b.get("distance", 0)),
                    "id": b.get("id"),
                })
        return results
