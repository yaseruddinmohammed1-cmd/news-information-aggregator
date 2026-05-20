import requests
from typing import List
from models import Article


class NewsAPIClient:
    """Handles communication with the News API."""

    BASE_URL = "https://gnews.io/api/v4/top-headlines"

    def __init__(self, api_key: str):
        # Store the API key provided by the user
        self.api_key = api_key

    def fetch_articles(
        self,
        category: str = "technology",
        country: str = "us",
        page_size: int = 10
    ) -> List[Article]:
        """
        Fetches news articles from the News API
        and converts them into Article objects.
        """

        # Stop execution if no API key is provided
        if not self.api_key:
            raise ValueError("API key is required.")

        # Parameters required by the News API request
        params = {
            "token": self.api_key,
            "topic": category,
            "lang": "en",
            "country": country,
            "max": page_size,
        }

        # Send request to the API
        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=15
        )

        # Raise an error if the request fails
        response.raise_for_status()

        # Convert API response to JSON format
        data = response.json()

        # Store all articles here after processing
        articles = []

        # Loop through each article returned by the API
        for item in data.get("articles", []):

            article = Article(
                title=item.get("title", "No title"),
                source=item.get("source", {}).get("name", "Unknown"),
                url=item.get("url", ""),
                published_at=item.get("publishedAt", ""),
                description=item.get("description") or "",
                author="Unknown",  # GNews often does not provide author
                content=item.get("content") or "",
                category=category,
            )

            # Add article object to the list
            articles.append(article)

        return articles