from lunchgenie.restaurant_provider import RestaurantProvider
from tools.yelp import YelpPlugin

class YelpProvider(RestaurantProvider):
    def __init__(self, config):
        self.plugin = YelpPlugin(config)

    def search_restaurants(self, query, location, criteria, latitude=None, longitude=None):
        # This simply wraps the YelpPlugin search
        # Note: YelpPlugin expects categories as a string, radius in meters, rating, etc.
        return self.plugin.search_restaurants(
            query=query,
            location=location,
            criteria=criteria,
            latitude=latitude,
            longitude=longitude
        )
