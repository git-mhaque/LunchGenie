from abc import ABC, abstractmethod

class RestaurantProvider(ABC):
    @abstractmethod
    def search_restaurants(
        self,
        query: str,
        location: str,
        criteria: dict,
        latitude: float = None,
        longitude: float = None
    ):
        """
        Returns a list of restaurant dicts based on searching with given parameters.
        """
        pass
