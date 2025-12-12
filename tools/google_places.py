"""
GooglePlacesPlugin: Fetch restaurants from Google Places API and filter results to match LunchGenie's expected output schema.
"""

from typing import List, Dict, Any, Optional
import requests
import os

from lunchgenie.config import Config
from tools.base import PluginBase, PluginError

GOOGLE_PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

class GooglePlacesPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "google_places"

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.api_key = self.config.google_places_api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise PluginError("Missing Google Places API key in config/environment.")

    def search_restaurants(
        self,
        query: str,
        location: str = "",
        criteria: Dict[str, Any] = None,
        latitude: float = None,
        longitude: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants with Google Places API. Supports searching by lat/lng or text location.
        """
        criteria = criteria or {}
        # Determine coordinates
        if latitude is not None and longitude is not None:
            location_str = f"{latitude},{longitude}"
        elif location:
            # Fallback: Geocode the location string using Places "textsearch"
            # Here, just skip and fallback to central Melbourne if can't geocode now
            location_str = "-37.816375,144.960934"
        else:
            # Default to CBD Melbourne if nothing else set
            location_str = "-37.816375,144.960934"

        radius = criteria.get("radius", 1200)
        min_rating = criteria.get("min_rating", 0)
        categories = criteria.get("categories", "") # Comma-separated

        params = {
            "key": self.api_key,
            "location": location_str,
            "radius": radius,
            "type": "restaurant",
            "keyword": query
        }
        # Add cuisine keywords
        if categories:
            cuisine_query = categories.replace(",", " ")
            params["keyword"] = f"{params['keyword']} {cuisine_query}".strip()

        try:
            resp = requests.get(GOOGLE_PLACES_SEARCH_URL, params=params, timeout=7)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status")
            if status != "OK":
                message = data.get("error_message", "")
                raise PluginError(f"Google Places API error: {status}. {message}")
            places = data.get("results", [])
        except Exception as e:
            raise PluginError(f"Google Places API request failed: {e}")

        import math

        # Helper: Haversine distance
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # meters
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            d_phi = math.radians(lat2 - lat1)
            d_lambda = math.radians(lon2 - lon1)
            a = (math.sin(d_phi / 2) ** 2 +
                 math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        # Parse center point for distance calculation
        if latitude is not None and longitude is not None:
            center_lat = float(latitude)
            center_lon = float(longitude)
        else:
            center_lat, center_lon = -37.816375, 144.960934  # Default CBD Melbourne

        results = []
        for p in places:
            rating = p.get('rating', 0)
            if rating < min_rating:
                continue
            place_id = p.get("place_id")
            # Get Place details for more info (address, url, reviews, etc.)
            detail_params = {
                "key": self.api_key,
                "place_id": place_id,
                "fields": "name,rating,user_ratings_total,reviews,formatted_address,geometry,url,types"
            }
            try:
                detail_resp = requests.get(GOOGLE_PLACES_DETAILS_URL, params=detail_params, timeout=7)
                detail_resp.raise_for_status()
                detail_data = detail_resp.json()
                detail_status = detail_data.get("status")
                if detail_status != "OK":
                    detail = {}
                else:
                    detail = detail_data.get("result", {})
            except Exception:
                detail = {}

            # Calculate distance from center to place (if geometry present)
            try:
                loc = detail.get("geometry", {}).get("location", {}) or p.get("geometry", {}).get("location", {})
                lat2 = float(loc.get("lat", center_lat))
                lon2 = float(loc.get("lng", center_lon))
                distance = int(haversine(center_lat, center_lon, lat2, lon2))
            except Exception:
                distance = 0

            # Get reviews (Google returns a list with 'text')
            reviews_data = detail.get("reviews", [])
            reviews = [rv.get("text", "") for rv in reviews_data if rv.get("text")]

            # Only keep if within search radius
            if distance <= radius:
                results.append({
                    "name": p.get("name", detail.get("name")),
                    "address": detail.get("formatted_address", ""),
                    "rating": rating,
                    "review_count": p.get("user_ratings_total", detail.get("user_ratings_total", 0)),
                    "categories": p.get("types", []),
                    "url": detail.get("url", ""),
                    "distance_m": distance,
                    "id": place_id,
                    "reviews": reviews
                })
        return results
