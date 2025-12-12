"""
LunchGenie LLM agent core.
Initializes LangChain with OpenAI and offers basic LLM interaction.
Implements full agent workflow to recommend lunch places.
"""

from lunchgenie.config import Config, ConfigError
from lunchgenie.review_analyzer import ReviewAnalyzer

from langchain_openai import ChatOpenAI
import requests
import time

from tools.yelp import YelpPlugin
from tools.google_places import GooglePlacesPlugin

YELP_BUSINESS_DETAIL_URL = "https://api.yelp.com/v3/businesses/{id}/reviews"

def test_llm():
    """
    Sanity check for LangChain + OpenAI configuration.
    Runs a 'Hello, LunchGenie!' prompt via ChatOpenAI.
    """
    cfg = Config()
    llm = ChatOpenAI(
        openai_api_key=cfg.openai_api_key,
        model_name="gpt-3.5-turbo",
        temperature=0.2,
    )
    prompt = "Hello, LunchGenie! Reply with 'Hello, world!' if you are working."
    response = llm.invoke(prompt)
    return response.content

def recommend_lunch_places(
    cuisine_list=("chinese", "indian", "malaysian","italian"),
    min_rating=4.0,
    max_distance_m=3000,
    location="Melbourne",
    latitude=None,
    longitude=None
):
    """
    Main workflow: searches, filters, and summarizes best lunch options.
    Prints recommendations.

    Location selection logic:
        - If latitude & longitude are explicitly provided, use those.
        - Else, if location is not set (or set to None/"") but config has default lat/lon, use those.
        - Otherwise, use the string location as before (default "Melbourne").
    """
    cfg = Config()
    # Dynamically select provider
    if cfg.restaurant_provider == "yelp":
        provider = YelpPlugin(cfg)
    elif cfg.restaurant_provider == "google":
        provider = GooglePlacesPlugin(cfg)
    else:
        raise ValueError(f"Unknown RESTAURANT_PROVIDER: {cfg.restaurant_provider}")

    review_ai = ReviewAnalyzer(cfg)

    # Resolve location/coordinates
    use_lat = latitude
    use_lon = longitude
    use_loc = location

    # Prefer explicit lat/lon, then config defaults if not overridden
    if use_lat is None or use_lon is None:
        cfg_lat = cfg.default_latitude
        cfg_lon = cfg.default_longitude
        if (cfg_lat and cfg_lon) and (not location or location == "Melbourne"):
            try:
                use_lat = float(cfg_lat)
                use_lon = float(cfg_lon)
                use_loc = None  # Don't pass location if using lat/lon
            except Exception:
                # Fallback: ignore config values if not casts
                pass

    # Step 1: Find candidates
    criteria = {
        "categories": ",".join(cuisine_list),
        "min_rating": min_rating,
        "radius": max_distance_m
    }
    # Use new lat/lon support if possible
    try:
        results = provider.search_restaurants(
            query="ambient places for team lunch",
            location=use_loc if use_loc else "",
            criteria=criteria,
            latitude=use_lat,
            longitude=use_lon
        )
    except Exception as err:
        from tools.base import PluginError
        if isinstance(err, PluginError):
            print(f"Provider error: {err}")
            return
        else:
            print(f"Unexpected provider error: {err}")
            return
    if not results:
        print("No suitable restaurants found via provider.")
        return

    print(f"Found {len(results)} high-rated options. Analyzing reviews...")

    # Step 2: For each, get reviews & analyze
    good_places = []
    for entry in results:
        # Provider-independent review extraction
        reviews = []
        if "reviews" in entry and entry["reviews"]:
            # Use reviews supplied by provider (Google)
            reviews = entry["reviews"]
        elif cfg.restaurant_provider == "yelp":
            # Fetch reviews via Yelp API
            try:
                detail_url = YELP_BUSINESS_DETAIL_URL.format(id=entry["id"])
                headers = {"Authorization": f"Bearer {cfg.yelp_api_key}"}
                resp = requests.get(detail_url, headers=headers, timeout=7)
                resp.raise_for_status()
                reviews = [r["text"] for r in resp.json().get("reviews", [])]
            except Exception:
                reviews = []
        # else reviews stays empty

        summary = "No reviews to analyze."
        print(f"Analyzing reviews for {entry.get('name','?')} ({len(reviews)}).")
        analysis = review_ai.detect_red_flags(reviews)
        safe = analysis.get("safe", False)
        if safe:
            summary = analysis.get("summary", "") if analysis.get("summary", "") else summary
            entry["review_summary"] = summary
            good_places.append(entry)
        # Sleep a bit to stay under Yelp API rate limits and OpenAI usage quotas
        time.sleep(0.7)
    
    # Step 3: Select and present top ~5
    if not good_places:
        print("All matched places have review red flags or could not be verified as safe.")
        return
    good_places = sorted(good_places, key=lambda x: x["rating"], reverse=True)[:5]
    print("\nRecommended team lunch places (clean reviews, high rating, short walk):\n")
    for p in good_places:
        print(f"- {p['name']} ({', '.join(p['categories'])})")
        print(f"  Rating: {p['rating']} from {p['review_count']} reviews; {p['distance_m']}m from point.")
        print(f"  Address: {p['address']}")
        print(f"  More: {p['url']}")
        if "review_summary" in p:
            print(f"  Review summary: {p['review_summary']}")
        print("")

if __name__ == "__main__":
    # CLI test entrypoint (choose ONE: test LLM OR recommend demo)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "recommend":
        recommend_lunch_places()
    else:
        try:
            print("Testing LangChain + OpenAI integration...")
            result = test_llm()
            print(f"LLM Response: {result}")
        except ConfigError as ce:
            print(f"Configuration error: {ce}")
        except Exception as e:
            print(f"Unexpected error: {e}")
