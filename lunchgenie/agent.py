"""
LunchGenie LLM agent core.
Initializes LangChain with OpenAI and offers basic LLM interaction.
Implements full agent workflow to recommend lunch places.
"""

from lunchgenie.config import Config, ConfigError
from lunchgenie.review_analyzer import ReviewAnalyzer

import requests
import time

from lunchgenie.restaurant_provider.yelp_provider import YelpProvider
from lunchgenie.restaurant_provider.google_provider import GoogleProvider
from lunchgenie.llm_utils import test_llm
from lunchgenie.location_utils import resolve_location
from lunchgenie.review_fetcher import ReviewFetcher

class Agent:
    def __init__(self, config=None):
        self.cfg = config if config else Config()
        self.review_ai = ReviewAnalyzer(self.cfg)
        self.review_fetcher = ReviewFetcher(self.cfg)
        if self.cfg.restaurant_provider == "yelp":
            self.provider = YelpProvider(self.cfg)
        elif self.cfg.restaurant_provider == "google":
            self.provider = GoogleProvider(self.cfg)
        else:
            raise ValueError(f"Unknown RESTAURANT_PROVIDER: {self.cfg.restaurant_provider}")

    def recommend_lunch_places(self,
                               cuisine_list=("chinese", "indian", "malaysian","italian"),
                               min_rating=4.0,
                               max_distance_m=3000,
                               location="Melbourne",
                               latitude=None,
                               longitude=None):
        """
        High-level workflow: searches, filters, and summarizes lunch options.
        Returns clean recommendations for formatting/display.
        """
        use_loc, use_lat, use_lon = resolve_location(self.cfg, location, latitude, longitude)
        criteria = {
            "categories": ",".join(cuisine_list),
            "min_rating": min_rating,
            "radius": max_distance_m
        }
        try:
            results = self.provider.search_restaurants(
                query="ambient places for team lunch",
                location=use_loc if use_loc else "",
                criteria=criteria,
                latitude=use_lat,
                longitude=use_lon
            )
        except Exception as err:
            from tools.base import PluginError
            if isinstance(err, PluginError):
                return f"Provider error: {err}"
            else:
                return f"Unexpected provider error: {err}"
        if not results:
            return None
        # Analyze reviews and filter
        good_places = []
        
        print(f"Found {len(results)} high-rated options. Analyzing reviews...")

        for entry in results:
            name = entry.get('name', '?')
            print(f"Analyzing reviews for {name} ...")
            reviews = self.review_fetcher.get_reviews(entry)
            analysis = self.review_ai.detect_red_flags(reviews)
            safe = analysis.get("safe", False)
            if safe:
                summary = analysis.get("summary", "") if analysis.get("summary", "") else "No reviews to analyze."
                entry["review_summary"] = summary
                good_places.append(entry)
            time.sleep(0.7)
        if not good_places:
            return []
        good_places = sorted(good_places, key=lambda x: x["rating"], reverse=True)[:5]
        return good_places

def recommend_lunch_places(
    cuisine_list=("chinese", "indian", "malaysian","italian"),
    min_rating=4.0,
    max_distance_m=3000,
    location="Melbourne",
    latitude=None,
    longitude=None
):
    agent = Agent()
    recommendations = agent.recommend_lunch_places(
        cuisine_list=cuisine_list,
        min_rating=min_rating,
        max_distance_m=max_distance_m,
        location=location,
        latitude=latitude,
        longitude=longitude
    )
    # Formatting/printing responsibility no longer in core agent
    return recommendations
