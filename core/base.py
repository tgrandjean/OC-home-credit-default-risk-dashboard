"""base: contains mother classes for component."""

from abc import ABC, abstractmethod
import requests

class Component(ABC):

    def __init__(self, API_URL, API_KEY):
        """Component

        Inherit this class for extras components.
        """
        self.API_KEY = API_KEY
        self.API_URL = API_URL

    @property
    def headers(self):
        """Return the header for requests."""
        return {'Content-Type': 'application/json',
                'Authorization': 'Token ' + self.API_KEY}

    def _fetch_application(self, id):
        res = requests.get(self.API_URL + f'/applications/{id}',
                           headers=self.headers)
        return res.json()

    @abstractmethod
    def form(self):
        """Override this method."""
        pass
