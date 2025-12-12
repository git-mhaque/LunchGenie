"""
Base class and interface for all LunchGenie restaurant data plugins.

All plugins MUST inherit from PluginBase and implement the search_restaurants method.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PluginError(Exception):
    pass

class PluginBase(ABC):
    """
    Abstract interface for restaurant data-source plugins.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier (e.g., 'yelp', 'google_places')"""
        pass

    @abstractmethod
    def search_restaurants(
        self, 
        query: str, 
        location: str = '', 
        criteria: Dict[str, Any] = None, 
        latitude: float = None, 
        longitude: float = None
    ) -> List[Dict[str, Any]]:
        """
        Query for restaurants given user constraints.

        :param query: Short string like 'Asian restaurant'
        :param location: Free-form location/address/text or coordinates
        :param criteria: Dict of filtering constraints (rating, cuisine, distance, etc.)
        :param latitude: Optional latitude for search center
        :param longitude: Optional longitude for search center
        :return: List of restaurant dicts (standard schema with at least name, address, rating, url)
        :raises PluginError: for API/key issues, quota, or validation errors
        """
        pass
