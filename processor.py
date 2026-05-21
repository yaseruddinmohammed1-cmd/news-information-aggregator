import pandas as pd
from typing import List
from models import Article


class NewsProcessor:
    """
    Handles data conversion, cleaning, and preparation
    for news articles before visualization and display.
    """

    def to_dataframe(self, articles: List[Article]) -> pd.DataFrame:
        """
        Converts a list of Article objects into a pandas DataFrame.
        This makes the data easier to clean, analyze, and visualize.
        """

        # Convert each Article object into dictionary format
        data = [article.__dict__ for article in articles]

        # Create and return the dataframe
        return pd.DataFrame(data)

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the dataframe by:
        - removing duplicates
        - handling missing values
        - formatting publication dates
        """

        # Return immediately if dataframe is empty
        if df.empty:
            return df

        # Create a copy to avoid modifying the original dataframe
        df = df.copy()

        # Remove duplicate articles using title and URL
        df = df.drop_duplicates(subset=["title", "url"])

        # Fill missing values with readable default values
        df["source"] = df["source"].fillna("Unknown")
        df["author"] = df["author"].fillna("Unknown")
        df["description"] = df["description"].fillna("")
        df["content"] = df["content"].fillna("")

        # Convert published date into proper datetime format
        df["published_at"] = pd.to_datetime(
            df["published_at"],
            errors="coerce"
        )

        return df