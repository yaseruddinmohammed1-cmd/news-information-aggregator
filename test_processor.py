import pandas as pd
from processor import NewsProcessor


def test_clean_data_removes_duplicate_articles():
    # Create a small sample dataset with the same article repeated twice
    processor = NewsProcessor()

    raw_data = pd.DataFrame({
        "title": ["A", "A"],
        "url": ["https://example.com/a", "https://example.com/a"],
        "source": ["Test", "Test"],
        "author": [None, None],
        "description": [None, None],
        "content": [None, None],
        "published_at": [
            "2026-01-01T00:00:00Z",
            "2026-01-01T00:00:00Z"
        ],
    })

    cleaned_data = processor.clean_data(raw_data)

    # Only one copy of the article should remain after cleaning
    assert len(cleaned_data) == 1

    # Missing author values should be replaced with a readable default value
    assert cleaned_data.iloc[0]["author"] == "Unknown"


def test_clean_data_handles_empty_dataframe():
    # The processor should not fail when there is no data to clean
    processor = NewsProcessor()

    cleaned_data = processor.clean_data(pd.DataFrame())

    assert cleaned_data.empty