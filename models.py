from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    """
    Represents a single news article used throughout the application.

    This class helps keep article data structured and makes
    the code easier to manage using object-oriented principles.
    """

    # Main article title
    title: str

    # News source name (example: BBC, CNN, Reuters)
    source: str

    # Direct link to the original article
    url: str

    # Date and time when the article was published
    published_at: str

    # Short summary of the article
    description: Optional[str] = ""

    # Author name (if available from the API or scraping)
    author: Optional[str] = "Unknown"

    # Full article content or scraped preview text
    content: Optional[str] = ""

    # Category selected by the user (technology, business, sports, etc.)
    category: Optional[str] = "general"