# News Information Aggregator

**Subject:** 36122 Python Programming — Autumn 2026  
**Assessment:** Group Assignment — Project Report  
**App Link:** https://news-information-aggregator-nxecada88p5c2mtourejux.streamlit.app/

---

**Group Members**

| Member | ID | Role | Files |
|---|---|---|---|
| Yaser | 26039281 | API + Web Scraping | api_handler.py, app.py, requirements.txt |
| Adrian | 25585403 | Processing + Visualisation | processor.py, scraper.py, models.py |
| Yogesh Sajith Kumar | 25964343 | GUI + Testing + Integration | visualizer.py, test_processor.py, report.md |

---

## 1. Project Overview

The News Information Aggregator is a Python application built to collect, enrich, clean, and present current news article data through an interactive web interface. The system retrieves live headlines from the GNews public REST API, supplements each result with paragraph content scraped directly from the original source webpage where accessible, and passes the combined data through a cleaning pipeline before presenting it to the user. The final interface supports category and country filtering, article search, three visual breakdowns, and a downloadable CSV export.

The motivation behind the project was to build something that goes beyond a basic API wrapper. Raw API responses frequently contain truncated content, missing fields, and duplicate entries from syndicated stories. By combining API retrieval with web scraping and a structured cleaning stage, the application produces a dataset that is genuinely more useful than what either source provides independently. The workflow moves in a single direction: api_handler.py produces Article objects from the GNews response, scraper.py optionally enriches their content field, processor.py converts and cleans them into a DataFrame, visualizer.py generates charts from that DataFrame, and app.py coordinates everything within the Streamlit interface.

The codebase spans seven Python files. The shared data structure underpinning all modules is the Article dataclass defined in models.py, which was the first file committed to the project. Establishing a fixed shared contract before writing any individual module meant that when the components were integrated in app.py, data flowed through the pipeline without field name conflicts or type mismatches.

---

## 2. Design Decisions

### 2.1 Modular, One Class Per File Structure

The application was organised so that each major responsibility sits inside its own dedicated class and file. This was a deliberate decision rather than a default. When a project combines network requests, HTML parsing, data cleaning, chart generation, and interface logic in a single script, a bug in any one area can be difficult to isolate and fixing it risks breaking unrelated functionality. Separating these concerns means that a failure points directly to one file, individual components can be tested without instantiating the rest of the system, and any module can be replaced or extended without touching others.

The table below summarises how responsibilities were divided.

| File | Class | Responsibility |
|---|---|---|
| models.py | Article | Shared dataclass representing a single news article across all modules |
| api_handler.py | NewsAPIClient | GNews API communication, parameter mapping, JSON to Article conversion |
| scraper.py | ArticleScraper | Webpage access, BeautifulSoup paragraph extraction, fallback handling |
| processor.py | NewsProcessor | DataFrame construction, deduplication, null filling, date parsing |
| visualizer.py | NewsVisualizer | Matplotlib figure generation for bar, line and pie charts |
| app.py | Streamlit script | Module orchestration, user input handling, tab and display logic |
| test_processor.py | pytest functions | Automated unit tests for the NewsProcessor cleaning pipeline |

### 2.2 The Article Dataclass as a Shared Contract

When multiple modules in a pipeline produce and consume the same data, one of the most common sources of integration bugs is inconsistent assumptions about field names and types. To prevent this, the Article dataclass in models.py was defined before any other module was written and treated as the fixed interface that all other modules wrote against.

```python
@dataclass
class Article:
    title: str
    source: str
    url: str
    published_at: str
    description: Optional[str] = ""
    author: Optional[str] = "Unknown"
    content: Optional[str] = ""
    category: Optional[str] = "general"
```

Using a dataclass rather than a plain dictionary provides automatic initialisation from field annotations, a built-in `__dict__` attribute that NewsProcessor uses to convert Article objects into a DataFrame without custom serialisation, and explicit type annotations that make each field's expected type clear to anyone reading the code. The four required fields correspond to values GNews always returns. Optional fields default to empty strings or "Unknown" so that Article construction never fails on a partial API response. The content field is the only one updated after construction, overwritten by the scraper when page scraping returns usable text.

### 2.3 Choosing Streamlit Over Tkinter

Streamlit was selected as the interface framework rather than Tkinter for three reasons. First, Streamlit produces a browser-based application rather than a desktop window, which is more appropriate for a system centred on web data. Second, it can be deployed publicly to Streamlit Community Cloud with minimal configuration, making the application accessible without requiring the evaluator to install dependencies locally. Third, it provides purpose-built widgets for the kinds of inputs this application needs — password fields, dropdowns, sliders, and tabbed layouts — that would require considerably more boilerplate to replicate in Tkinter. The tradeoff is that Streamlit's execution model reruns the full script on every user interaction, which required gating all API fetch logic behind `st.button()` to prevent redundant network calls when the user adjusts sidebar settings.

### 2.4 Choosing BeautifulSoup Over Scrapy

BeautifulSoup was selected for the scraping layer rather than Scrapy because the scraping requirement in this application is narrow in scope. Each fetch retrieves a small number of article URLs and extracts only paragraph text from each page. Scrapy is a full crawling framework designed for large-scale, asynchronous multi-page spiders and introduces considerable architectural overhead for a use case that requires a single synchronous request per article. BeautifulSoup paired with the requests library is sufficient for this purpose, easier to integrate into an existing synchronous pipeline, and straightforward to wrap in exception handling.

### 2.5 Web Scraping Strategy

The scraper was designed to limit extracted content to a 1,500-character paragraph preview rather than reproducing full article text. This decision reflects both practical and ethical considerations. Practically, full article text would overwhelm the article explorer interface and make the CSV export unwieldy. Ethically, a short preview for personal research purposes is more defensible under fair use principles than wholesale reproduction of published content. The scraper includes a browser-style User-Agent header to reduce rejection by sites with basic bot filtering, and the entire method is enclosed in a broad exception block so that any failure — whether a network timeout, an HTTP error, or a JavaScript-rendered page — returns a controlled fallback string and allows the rest of the pipeline to continue unaffected.

### 2.6 GNews as the Data Source

GNews was chosen over alternatives such as NewsAPI because it provides a free tier that supports both topic and country filtering in a single request without requiring credit card registration. The top-headlines endpoint returns well-structured JSON with consistent field names, and the combination of category and country parameters allows the same application to produce meaningfully different outputs across a wide range of queries. One limitation of the free tier is a cap on daily requests and a maximum of ten articles per call; the article count slider in the interface extends to twenty to accommodate users on paid plans.

---

## 3. Main System Components

### API Handling

The NewsAPIClient class in api_handler.py sends requests to the GNews top-headlines endpoint at `https://gnews.io/api/v4/top-headlines`. The API key is stored as an instance attribute during initialisation, and the single public method `fetch_articles()` accepts category, country, and page_size as parameters that map directly to the topic, country, and max query parameters in the request. A pre-flight check raises a ValueError if the key string is empty, preventing an unauthenticated request before any network call is made. After the request, `response.raise_for_status()` converts any 4xx or 5xx HTTP status into a Python exception. Both errors propagate to app.py's top-level try-except block where they appear as a Streamlit error message.

Each item in the JSON response is mapped to an Article instance using `.get()` with fallback values throughout, so missing or null keys never raise a KeyError. The source field in GNews is a nested dictionary containing a name key, accessed via a chained `.get()` call. The `or ""` pattern on description and content handles null JSON values, since `None or ""` evaluates to an empty string and ensures both fields are always strings when the Article object is constructed.

### Web Scraping

The ArticleScraper class in scraper.py accesses each article URL using requests and parses the returned HTML with BeautifulSoup to extract paragraph text. The method collects the first eight paragraph elements using `find_all("p")`, joins them with `get_text(strip=True)` to remove inner HTML tags and whitespace, and truncates the result to 1,500 characters. Because many news websites block automated requests or load content dynamically through JavaScript, the entire method is wrapped in a broad except block. Any failure returns the fallback string rather than raising an exception into app.py's scraping loop. In app.py, scraped text only replaces the article's content field when it is non-empty and not equal to the fallback string, ensuring the original API content is always preserved when scraping is unsuccessful.

### Data Processing

The NewsProcessor class in processor.py converts the list of Article objects into a pandas DataFrame by calling `__dict__` on each instance, producing a list of plain dictionaries that `pd.DataFrame()` converts into a structured table. The `clean_data()` method then applies five operations to address data quality issues observed in real GNews responses.

An empty guard returns the DataFrame immediately if it contains no rows, preventing KeyError when column operations are applied to a table with no columns. A deep copy via `df.copy()` avoids mutating the caller's DataFrame, which is necessary for repeatable unit test results. Deduplication uses both title and URL as a composite key to avoid incorrectly removing articles from different sources that happen to share a headline. Null filling assigns "Unknown" to source and author for readable display, and empty strings to description and content to prevent TypeError in string operations used in the article explorer. Date parsing uses `pd.to_datetime()` with `errors="coerce"` to convert ISO 8601 strings to Timestamp objects; without this, accessing `.dt.date` in the visualiser raises AttributeError. Unparseable values become NaT silently and are dropped before chart rendering.

### Data Visualisation

The NewsVisualizer class in visualizer.py produces three Matplotlib charts, each returned as a Figure object rather than rendered inline. Returning figures rather than calling `plt.show()` keeps the class decoupled from the rendering environment; Streamlit receives each Figure and renders it via `st.pyplot()`, but the same methods would work unchanged in a Jupyter notebook or any other Python context.

The horizontal bar chart shows article counts for the top ten sources, sorted ascending so the most prolific publisher appears at the top. Source names are too long for a vertical axis without label overlap, which is why a horizontal layout was used. Value labels are appended beside each bar so users can read exact counts without estimating against the grid.

The line chart shows articles published per day. NaT values are dropped first, the date component is extracted using `.dt.date`, articles are grouped by date, and the daily count is plotted with circle markers. Markers are necessary because GNews responses typically span a narrow two to three day window where a plain line with no markers would be difficult to read.

The pie chart shows the proportional share of the top six sources, with each slice labelled with its percentage using `autopct="%1.1f%%"`. The limit of six prevents the chart from becoming unreadable when results come from many small outlets.

A fourth element in the Dashboard tab is a source summary table built in app.py from `df["source"].value_counts()` and rendered via `st.dataframe()`. Together the three charts and the table answer four distinct questions: which sources appear, on which days, in what proportion, and with what exact counts.

### Graphical User Interface

The app.py file coordinates the full application through Streamlit. All user configuration is placed in a sidebar block, keeping the main panel clear for results. Five input widgets are provided: a password-masked API key field, a category dropdown covering seven GNews topic values, a country selector for five English-language markets, an article count slider from five to twenty, and a scraping toggle checkbox. All fetch logic is gated behind `st.button()`, which only returns True during the specific re-execution triggered by clicking the button, preventing redundant API calls when the user changes sidebar settings or switches tabs after an initial fetch. A spinner displays a loading animation during fetching and scraping, which can collectively take fifteen to thirty seconds across twenty articles. After processing, three metric cards show total article count, unique source count, and unknown author count before the tab content loads.

Results are organised across four tabs. The Dashboard tab renders the three charts and the source summary table. The Dataset tab displays the cleaned DataFrame with interactive column sorting. The Articles tab provides a real-time case-insensitive title search using `str.contains()`, with each matching article shown as an expander card containing source, author, date, description, content preview, and URL. The Export tab offers a download button that encodes the cleaned DataFrame as a UTF-8 CSV file. Before any fetch is triggered, a welcome screen describes the application and outlines the four-step workflow.

### Unit Testing

Automated testing focused on the NewsProcessor class using pytest, as data cleaning is the stage most likely to produce silent errors if edge cases are not handled. The test suite in test_processor.py covers two scenarios.

The first test constructs a DataFrame with two identical rows sharing the same title and URL, runs `clean_data()`, and asserts that only one row remains after deduplication. It also asserts that the None author value has been replaced with "Unknown", covering both the `drop_duplicates()` and `fillna()` logic in a single case.

The second test passes a completely empty DataFrame to `clean_data()` and confirms that the result is still empty and that no exception is raised, verifying the early return guard that prevents downstream operations from running on a table with no columns.

Both tests passed successfully on every run throughout development.

---

## 4. Challenges and How They Were Addressed

### Web Scraping Restrictions

The most significant technical obstacle encountered during development was the inconsistency of web scraping outcomes across different news websites. A substantial proportion of publishers block automated HTTP requests through User-Agent inspection, rate limiting, or Cloudflare bot protection. Others load article content dynamically through JavaScript, which means the HTML returned by a standard GET request contains only the page skeleton and no readable paragraph text. BeautifulSoup works on the initial HTTP response only and cannot execute JavaScript, making these pages effectively inaccessible through the chosen approach.

The decision was made early to treat scraping failure as an expected outcome rather than an error condition. The entire scraping method is enclosed in a broad exception handler that returns a controlled fallback string on any failure, whether a network timeout, an HTTP error response, or an empty paragraph result. In app.py, the article content field is only overwritten when the scraped result is non-empty and not equal to the fallback string, so the original API snippet is always preserved when scraping does not succeed. A sidebar checkbox gives users the option to disable scraping entirely for faster fetches when content enrichment is not the priority.

### GNews Free Tier Rate Limits

The GNews free tier imposes a cap on daily API requests and returns a maximum of ten articles per call regardless of the max parameter value. This constrained testing during development because exhausting the daily quota meant waiting until the following day to run further integration tests. The article count slider was designed to extend to twenty to accommodate paid plan users, but the application behaves correctly within the ten-article limit of the free tier. Testing was structured to use small fetch counts wherever possible to preserve the daily allowance for end-to-end verification runs.

### Data Quality Issues in API Responses

Raw GNews responses consistently exhibited several data quality problems that required deliberate handling rather than assumption. Author fields are absent from the majority of responses because GNews does not reliably surface this information from publisher feeds. Descriptions vary considerably in length and are occasionally null rather than an empty string. Publication dates arrive as ISO 8601 formatted strings that must be converted to datetime objects before any date-based grouping or sorting can be applied. The same story frequently appears multiple times across different syndication sources with identical titles and URLs.

Each of these issues was addressed through a dedicated operation in the `clean_data()` method. The composite key deduplication on title and URL removes syndicated duplicates without incorrectly dropping articles from different publishers that happen to share a headline. The `fillna()` calls provide readable defaults for display rather than leaving NaN values that would surface as "nan" strings in the interface. The `pd.to_datetime()` conversion with `errors="coerce"` handles malformed timestamps without raising exceptions, silently converting unparseable values to NaT so they are excluded from chart grouping rather than causing a crash.

### Interface State Management

Streamlit's execution model reruns the full application script on every user interaction, including sidebar adjustments and tab switches. In early versions of the interface, this caused the API fetch logic to re-execute every time the user changed a dropdown value or clicked a different tab, producing redundant network requests and resetting the displayed results. The solution was to gate all fetch logic behind `st.button()`, which returns True only during the specific script execution triggered by clicking the Fetch News button and returns False on all other reruns. This means the application fetches data exactly when the user requests it and preserves the displayed results through subsequent interactions.

A secondary interface challenge was the blank main panel that appeared before any data was fetched. A purposeful welcome screen was added that describes the application, introduces its three core features, and outlines the four-step workflow. This ensures the interface communicates its purpose clearly to a user who arrives without prior context.

### Cross-Module Integration

Developing five separate modules independently created a risk of integration failures when they were brought together in app.py. The most likely failure mode was field name mismatches between what api_handler.py placed on an Article object and what processor.py expected to find when converting it to a DataFrame column. This risk was eliminated by treating the Article dataclass as a frozen interface defined before any individual module was written. When the modules were integrated, data flowed through the pipeline cleanly with no field name conflicts or type errors across any of the development test runs.

---

## 5. Additional Features

### Configurable Article Count

The number of articles retrieved per session is controlled by a slider ranging from five to twenty. This gives users flexibility over the volume of data processed in a single fetch and reflects consideration for both API quota management and scraping time. Fetching twenty articles with scraping enabled can take up to thirty seconds depending on individual site response times; the slider allows users to make an informed tradeoff between data volume and wait time.

### Category and Country Filtering

The sidebar exposes a category dropdown covering seven GNews topic values — business, entertainment, general, health, science, sports, and technology — alongside a country selector covering five English-language markets: the United States, Australia, the United Kingdom, Canada, and India. This combination allows the same application to produce meaningfully different outputs across a wide range of queries without any changes to the underlying code. A technology news fetch filtered to Australia, for example, returns a substantially different dataset from a sports news fetch filtered to the United States.

### Optional Web Scraping Toggle

Scraping can be enabled or disabled independently of the API fetch through a checkbox in the sidebar. When unchecked, the scraping loop in app.py is skipped entirely and the pipeline proceeds directly from the API response to data processing. This feature exists because scraping adds meaningful latency — a single unavailable site may wait the full ten-second request timeout before returning a failure — and because users who are interested only in headlines and metadata from the API response should not be required to wait for scraping they do not need.

### Article Search and Explorer

The Articles tab provides a live title search implemented using pandas `str.contains()` with `case=False`. As the user types into the search field, the displayed article list filters in real time to show only entries whose titles contain the search term. Each result is displayed as a Streamlit expander card that can be opened to reveal the article source, author, publication date, description, content preview enriched by scraping where available, and the original URL. This design allows users to locate specific articles of interest quickly within a larger dataset without requiring separate filtering tools.

### Summary Metric Cards

Immediately after a successful fetch and before the tab layout loads, three metric cards display the total number of articles retrieved, the number of unique sources represented in the results, and the count of entries where the author field could not be determined. These indicators give users an immediate quantitative sense of the dataset's shape and the degree to which author attribution is available, without requiring them to open any tab or inspect the raw DataFrame.

### CSV Export

The cleaned and processed DataFrame can be downloaded as a CSV file from the Export tab via a Streamlit download button. The file is encoded as UTF-8 and named news_articles.csv. This feature makes the application useful beyond its own interface, as exported data can be opened in spreadsheet software or passed to other analysis tools without any manual data extraction.

### Ethical Web Scraping Practices

The scraper was designed with explicit attention to the ethical boundaries of automated web access. It targets only publicly accessible article pages and makes no attempt to bypass paywalls, authentication systems, or explicit bot restrictions. When a website declines access, the application accepts that outcome gracefully through its exception handler and moves on without attempting any circumvention. The API key is entered at runtime through a password-masked input field rather than being stored in the source code, which prevents credential exposure through version control. Content extracted from article pages is limited to a short paragraph preview rather than full reproduction, which limits the extent to which scraped material is displayed and reduces concern around copyright.

---

## 6. Testing and Evaluation

Automated testing was applied to the NewsProcessor class using pytest. NewsProcessor was specifically selected for this treatment because it operates entirely on in-memory data structures with no external dependencies, meaning tests run in full isolation without requiring network access, API credentials, or mocking of external services. The test file is test_processor.py, located in the project root.

The first test case constructs a DataFrame containing two identical rows with the same title and URL, simulating the syndication duplicates commonly present in raw GNews responses. After running `clean_data()`, the test asserts that only one row remains, confirming that deduplication operates correctly. It additionally asserts that the None value in the author column has been replaced with the string "Unknown", confirming that null filling runs after deduplication and handles pre-existing None values rather than only NaN values introduced by pandas operations.

The second test case passes a completely empty DataFrame to `clean_data()` and asserts that the returned DataFrame is also empty. This test is important in a production context because GNews returns zero results for certain category and country combinations, and without the early return guard in `clean_data()`, the subsequent `drop_duplicates()` call would raise a KeyError on a DataFrame with no columns.

Both tests passed on every run throughout development. The value of the test suite extends beyond confirming that the current implementation is correct: it also provides a safety net for future changes, ensuring that any modification to the cleaning logic that breaks an existing behaviour will be caught immediately rather than surfacing as a silent data quality regression in production.

---

## 7. Conclusion

The News Information Aggregator demonstrates how several distinct Python capabilities — REST API communication, HTML parsing, structured data processing, data visualisation, and interactive interface development — can be integrated into a single coherent application that is genuinely useful rather than merely demonstrative. The system handles the full lifecycle of news data from retrieval through to user-facing presentation, with each stage designed to handle realistic failure conditions gracefully.

The most consequential architectural decision was defining the Article dataclass as a shared contract before any individual module was developed. This eliminated integration failures at combination time, kept field names consistent across independently written modules, and allowed parallel development without coordination overhead. The one-class-per-file structure reinforced single responsibility at the filesystem level and produced a codebase where each component can be understood, tested, and extended without reference to the others.

The challenges encountered during development — scraping restrictions, API rate limits, data quality inconsistencies, and interface state management — were addressed through deliberate design decisions rather than workarounds. The scraper treats failure as a normal outcome rather than an exception. The processor addresses each known data quality issue with a targeted operation that is independently verifiable through the unit test suite. The interface gates side-effect logic behind an explicit user action to prevent unintended re-execution. These decisions collectively produce a system that is stable under the kinds of inputs and failures it will encounter in real use.

The primary remaining limitation is the inability to scrape JavaScript-rendered article pages, which account for a significant proportion of modern news websites. The modular architecture accommodates a targeted response to this: replacing scraper.py with an implementation based on a headless browser such as Playwright would extend scraping coverage to these sites without requiring changes to any other module. This illustrates the practical value of the separation of concerns that was central to the project's design from the outset.

---

## Appendix: Dependencies and Setup

| Package | Used In | Purpose |
|---|---|---|
| streamlit | app.py | Web GUI framework for all interface components |
| requests | api_handler.py, scraper.py | HTTP client for API calls and article page access |
| beautifulsoup4 | scraper.py | HTML parsing for paragraph text extraction |
| pandas | processor.py, visualizer.py | DataFrame construction, cleaning, and date parsing |
| matplotlib | visualizer.py | Chart figure generation for all three visualisations |
| pytest | test_processor.py | Test runner for automated unit test discovery and execution |

**To run locally:** create a virtual environment, run `pip install -r requirements.txt`, then `streamlit run app.py`. Enter your GNews API key in the sidebar. Run `pytest` from the project root to execute all unit tests.

**Live deployment:** https://news-information-aggregator-nxecada88p5c2mtourejux.streamlit.app/
