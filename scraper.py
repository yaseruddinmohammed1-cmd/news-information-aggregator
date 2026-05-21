import requests
from bs4 import BeautifulSoup


class ArticleScraper:
    """
    Handles web scraping for additional article content.

    This helps collect extra information from the actual
    news webpage that may not be available from the API response.
    """

    def scrape_article_text(self, url: str) -> str:
        """
        Scrapes article text from the provided news article URL.

        The method extracts paragraph content from the webpage
        and returns a short readable preview.
        """

        try:
            # Add browser-like headers to reduce blocking by websites
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36"
                )
            }

            # Send request to the article webpage
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            # Raise an error if the request fails
            response.raise_for_status()

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # Extract paragraph tags from the page
            paragraphs = soup.find_all("p")

            # Combine the first few paragraphs into one text block
            text = " ".join(
                p.get_text(strip=True)
                for p in paragraphs[:8]
            )

            # Return shortened text for cleaner display in the app
            if text:
                return text[:1500]

            return "No extra scraped content available."

        except Exception:
            # Return fallback message if scraping fails
            return "Scraping failed or blocked by website."