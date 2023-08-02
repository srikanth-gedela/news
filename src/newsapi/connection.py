import requests
import pandas as pd
import streamlit as st

from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data

from typing import Any, Dict, Optional


class NewsAPIConnection(ExperimentalBaseConnection):
    """Handles connection with the NewsAPI to retrieve news articles."""

    def _connect(self):
        """Initializes parameters to connect with the NewsAPI."""
        self.key = st.secrets['NEWSAPI_KEY']
        self.base = st.secrets['NEWSAPI_BASE_URL']

    def _make_api_request(self, url: str) -> Optional[Dict[str, Any]]:
        """Makes a GET request to the provided URL and returns the parsed JSON response."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except (requests.exceptions.RequestException, ValueError) as e:
            st.error(f'Error: {e} for URL: {url}')
            return None

    def _to_dataframe(self, data: Optional[Dict[str, Any]]) -> Optional[pd.DataFrame]:
        """Converts data to a DataFrame containing 'Articles', handling the case of no articles found."""
        if data is None:
            return None

        articles = data.get('articles', None)
        return pd.DataFrame(articles)

    def query(self, topic: str, ttl: int = 3600) -> Optional[pd.DataFrame]:
        """
        Queries the NewsAPI for news articles on a given topic.
        Data is cached for a duration given by ttl.
        """

        @cache_data(ttl=ttl)
        def _query(topic: str) -> Optional[pd.DataFrame]:
            """Performs the actual API call and data processing."""
            url = f"{self.base}everything?q={topic}&apiKey={self.key}"

            data = self._make_api_request(url)
            return self._to_dataframe(data)

        return _query(topic)

    def top(self, country: str, category: str, ttl: int = 3600) -> Optional[pd.DataFrame]:
        """
        Queries the NewsAPI for top news articles in a given country (2-letter ISO 3166-1 code) and category.
        Data is cached for a duration given by ttl.
        """

        @cache_data(ttl=ttl)
        def _query(country: str, category: str) -> Optional[pd.DataFrame]:
            """Performs the actual API call and data processing."""
            url = f"{self.base}top-headlines?country={country}&category={category}&apiKey={self.key}"

            data = self._make_api_request(url)
            return self._to_dataframe(data)

        return _query(country, category)
