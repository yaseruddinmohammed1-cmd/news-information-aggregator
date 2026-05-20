# News Information Aggregator

This project is a Python-based News Information Aggregator. It uses a public News API to fetch article headlines, uses web scraping to extract additional article text, processes the data, visualizes news trends, and displays everything in a Streamlit GUI.

## Features

- Fetch current news articles using NewsAPI
- User can choose category, country, and number of articles
- Scrape extra article text using BeautifulSoup
- Clean and remove duplicate article records
- Display article dataset in a GUI
- Visualize article counts by source and publication date
- Download processed dataset as CSV
- Includes unit tests for data processing

## Technologies Used

- Python
- Streamlit
- Requests
- BeautifulSoup
- Pandas
- Matplotlib
- Pytest

## How to Run

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Streamlit app:

```bash
streamlit run app.py
```

5. Enter your GNews API Key in the sidebar.

## API Key

Create a free API key from NewsAPI.org and paste it into the Streamlit sidebar.

## Unit Testing

Run tests using:

```bash
pytest
```

## Ethical Web Scraping Note

This project only scrapes limited article preview text for educational purposes. Some websites may block scraping. Always respect robots.txt, website terms of service, and API rules.
