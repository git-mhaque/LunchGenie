from lunchgenie.restaurant_provider import RestaurantProvider
from tools.google_places import GooglePlacesPlugin

class GoogleProvider(RestaurantProvider):
    def __init__(self, config):
        self.plugin = GooglePlacesPlugin(config)

    def search_restaurants(self, query, location, criteria, latitude=None, longitude=None):
        # This wraps the GooglePlacesPlugin search
        return self.plugin.search_restaurants(
            query=query,
            location=location,
            criteria=criteria,
            latitude=latitude,
            longitude=longitude
        )
