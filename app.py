import streamlit as st
import pandas as pd

from api_handler import NewsAPIClient
from scraper import ArticleScraper
from processor import NewsProcessor
from visualizer import NewsVisualizer


# Page configuration
st.set_page_config(
    page_title="News Information Aggregator",
    page_icon="📰",
    layout="wide"
)


# Custom styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Main title
st.markdown(
    "<div class='main-title'>📰 News Information Aggregator</div>",
    unsafe_allow_html=True
)


# Sidebar settings
with st.sidebar:

    # API key input
    api_key = st.text_input(
        "GNews API Key",
        type="password"
    )

    # Category selection
    category = st.selectbox(
        "Choose news category",
        [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology"
        ],
        index=6
    )

    # Country selection
    country = st.selectbox(
        "Choose country",
        ["us", "au", "gb", "ca", "in"],
        index=0
    )

    # Article count selection
    article_count = st.slider(
        "Number of articles",
        min_value=5,
        max_value=20,
        value=10
    )

    # Optional scraping
    scrape_enabled = st.checkbox(
        "Scrape extra article text",
        value=True
    )


# Main fetch button
fetch_button = st.button(
    "🔍 Fetch News",
    use_container_width=True
)


if fetch_button:
    try:
        # Create objects from project classes
        client = NewsAPIClient(api_key)
        scraper = ArticleScraper()
        processor = NewsProcessor()
        visualizer = NewsVisualizer()

        # Fetch articles from API
        with st.spinner("Fetching news articles..."):
            articles = client.fetch_articles(
                category=category,
                country=country,
                page_size=article_count
            )

        # Scrape additional content if enabled
        if scrape_enabled:
            with st.spinner("Scraping additional article content..."):
                for article in articles:
                    scraped_text = scraper.scrape_article_text(article.url)

                    # Replace content only when scraping succeeds
                    if (
                        scraped_text
                        and scraped_text != "Scraping failed or blocked by website."
                    ):
                        article.content = scraped_text

        # Convert to dataframe and clean the data
        df = processor.to_dataframe(articles)
        df = processor.clean_data(df)

        # Stop if no articles are returned
        if df.empty:
            st.warning(
                "No articles found. Please try another category or country."
            )
            st.stop()

        st.success(
            f"Successfully fetched and processed {len(df)} articles."
        )

        # Summary values
        total_articles = len(df)
        unique_sources = df["source"].nunique()
        unknown_authors = (df["author"] == "Unknown").sum()

        # Summary section
        st.subheader("📊 News Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Articles", total_articles)
        col2.metric("Unique Sources", unique_sources)
        col3.metric("Unknown Authors", unknown_authors)

        st.divider()

        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Dashboard",
            "🗂 Dataset",
            "📰 Articles",
            "⬇️ Export"
        ])

        # Dashboard tab
        with tab1:
            st.subheader("📈 Visual Dashboard")

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown("### Top News Sources")
                st.pyplot(
                    visualizer.articles_by_source(df)
                )

            with chart_col2:
                st.markdown("### Publication Trend")
                st.pyplot(
                    visualizer.articles_over_time(df)
                )

            st.divider()

            chart_col3, chart_col4 = st.columns(2)

            with chart_col3:
                st.markdown("### Source Share")
                st.pyplot(
                    visualizer.source_pie_chart(df)
                )

            with chart_col4:
                st.markdown("### Source Summary")

                # Count articles by source
                source_summary = df["source"].value_counts().reset_index()
                source_summary.columns = ["News Source", "Articles"]

                st.dataframe(
                    source_summary,
                    use_container_width=True,
                    hide_index=True
                )

        # Dataset tab
        with tab2:
            st.subheader("Processed Dataset")

            display_columns = [
                "title",
                "source",
                "author",
                "published_at",
                "url",
                "category"
            ]

            available_columns = [
                col for col in display_columns
                if col in df.columns
            ]

            st.dataframe(
                df[available_columns],
                use_container_width=True,
                hide_index=True
            )

        # Articles tab
        with tab3:
            st.subheader("Article Explorer")

            search_text = st.text_input(
                "Search article title"
            )

            filtered_df = df.copy()

            # Filter article titles based on search input
            if search_text:
                filtered_df = filtered_df[
                    filtered_df["title"].str.contains(
                        search_text,
                        case=False,
                        na=False
                    )
                ]

            for _, row in filtered_df.iterrows():
                with st.expander(row["title"]):
                    st.write(f"**Source:** {row['source']}")
                    st.write(f"**Author:** {row['author']}")
                    st.write(f"**Published:** {row['published_at']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Content Preview:** {row['content']}")
                    st.write(f"**URL:** {row['url']}")

        # Export tab
        with tab4:
            st.subheader("Download Dataset")

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name="news_articles.csv",
                mime="text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Error: {e}")

        st.info(
            "Please check your GNews API Key and ensure it is active."
        )


else:
    # Home screen shown before fetching news
    st.markdown("### Welcome to the News Information Aggregator")

    st.info(
        "Enter your GNews API Key in the sidebar, choose your settings, "
        "then click Fetch News to begin."
    )

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔌 API Integration")
        st.write(
            "Fetches real-time news articles from a public News API "
            "based on your selected category and country."
        )

    with col2:
        st.markdown("### 🌐 Web Scraping")
        st.write(
            "Extracts additional article content from real news websites "
            "using BeautifulSoup for richer information."
        )

    with col3:
        st.markdown("### 📊 Data Visualization")
        st.write(
            "Displays article trends, source distribution, cleaned data, "
            "and downloadable CSV reports."
        )

    st.divider()

    # Workflow explanation
    st.markdown("### How It Works")

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        st.markdown("#### 1️⃣ Enter API Key")
        st.write("Provide your GNews API Key in the sidebar.")

    with step2:
        st.markdown("#### 2️⃣ Select Options")
        st.write("Choose category, country, and number of articles.")

    with step3:
        st.markdown("#### 3️⃣ Fetch News")
        st.write("The system collects articles and optional scraped content.")

    with step4:
        st.markdown("#### 4️⃣ Explore Results")
        st.write("View charts, article details, and export the dataset.")