import matplotlib.pyplot as plt
import pandas as pd


class NewsVisualizer:
    """
    Creates clean and professional visualizations
    for the processed news article dataset.
    """

    def articles_by_source(self, df: pd.DataFrame):
        """
        Creates a horizontal bar chart showing
        the number of articles by source.
        """

        fig, ax = plt.subplots(figsize=(9, 5))

        if df.empty:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            return fig

        # Count top news sources
        source_counts = df["source"].value_counts().head(10).sort_values()

        # Horizontal bars are easier to read than vertical bars
        source_counts.plot(
            kind="barh",
            ax=ax,
            color="#4C9AFF"
        )

        ax.set_title("Top News Sources", fontsize=14, fontweight="bold")
        ax.set_xlabel("Number of Articles")
        ax.set_ylabel("Source")

        # Add article count labels beside each bar
        for index, value in enumerate(source_counts):
            ax.text(value + 0.05, index, str(value), va="center")

        ax.grid(axis="x", linestyle="--", alpha=0.4)

        fig.tight_layout()
        return fig

    def articles_over_time(self, df: pd.DataFrame):
        """
        Creates a line chart showing article
        publication activity over time.
        """

        fig, ax = plt.subplots(figsize=(9, 5))

        if df.empty or "published_at" not in df.columns:
            ax.text(0.5, 0.5, "No date data available", ha="center", va="center")
            return fig

        temp = df.dropna(subset=["published_at"]).copy()

        if temp.empty:
            ax.text(0.5, 0.5, "No valid dates available", ha="center", va="center")
            return fig

        # Extract date only from publication timestamp
        temp["date"] = temp["published_at"].dt.date

        # Count articles per date
        date_counts = temp.groupby("date").size()

        date_counts.plot(
            kind="line",
            marker="o",
            linewidth=2.5,
            ax=ax,
            color="#FF6B6B"
        )

        ax.set_title("Article Publication Trend", fontsize=14, fontweight="bold")
        ax.set_xlabel("Publication Date")
        ax.set_ylabel("Number of Articles")

        ax.grid(True, linestyle="--", alpha=0.4)

        fig.tight_layout()
        return fig

    def source_pie_chart(self, df: pd.DataFrame):
        """
        Creates a pie chart showing the percentage
        distribution of articles by source.
        """

        fig, ax = plt.subplots(figsize=(7, 5))

        if df.empty:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
            return fig

        source_counts = df["source"].value_counts().head(6)

        ax.pie(
            source_counts,
            labels=source_counts.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title("Source Share", fontsize=14, fontweight="bold")

        fig.tight_layout()
        return fig