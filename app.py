from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    budget_vs_gross,
    correlation_heatmap,
    distribution,
    genre_count,
    genre_roi,
    profit_vs_score,
    tier_performance,
    yearly_trend,
)
from src.data_pipeline import (
    NUMERIC_COLUMNS,
    budget_tier_stats,
    clean_movies,
    correlation_pairs,
    financial_subset,
    genre_financial_stats,
    load_movies,
    summarize,
    top_movies,
)


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "movies.csv"


st.set_page_config(
    page_title="Movie Industry Intelligence",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def get_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_movies(DATA_PATH)
    clean = clean_movies(raw)
    return raw, clean


def format_money(value: float | int | None) -> str:
    if pd.isna(value):
        return "n/a"
    return f"${value:,.1f}M"


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year_range = st.sidebar.slider("Release year", year_min, year_max, (year_min, year_max))

    genres = sorted(df["genre"].dropna().unique().tolist())
    selected_genres = st.sidebar.multiselect("Genre", genres, default=genres)

    ratings = sorted(df["rating"].dropna().unique().tolist())
    selected_ratings = st.sidebar.multiselect("Rating", ratings, default=ratings)

    countries = sorted(df["country"].dropna().unique().tolist())
    default_countries = [country for country in ["United States", "United Kingdom", "Canada"] if country in countries]
    selected_countries = st.sidebar.multiselect("Country", countries, default=default_countries or countries[:5])

    min_score = st.sidebar.slider("Minimum IMDb score", 0.0, 10.0, 0.0, 0.1)

    mask = (
        df["year"].between(year_range[0], year_range[1])
        & df["genre"].isin(selected_genres)
        & df["rating"].isin(selected_ratings)
        & df["country"].isin(selected_countries)
        & (df["score"] >= min_score)
    )
    return df[mask].copy()


def build_markdown_report(df: pd.DataFrame) -> str:
    fin = financial_subset(df)
    genre_stats = genre_financial_stats(df, min_films=5)
    tier_stats = budget_tier_stats(df)
    top_gross = top_movies(df, "gross_M", 5)
    corr = correlation_pairs(df, "spearman").head(5)

    best_genre = genre_stats.iloc[0] if not genre_stats.empty else None
    best_tier = tier_stats.sort_values("median_roi", ascending=False).iloc[0] if not tier_stats.empty else None

    lines = [
        "# Movie Industry Intelligence Report",
        "",
        f"- Movies in current filter: {len(df):,}",
        f"- Financial-analysis movies: {len(fin):,}",
        f"- Average IMDb score: {df['score'].mean():.2f}",
        f"- Median gross: {format_money(df['gross_M'].median())}",
        f"- Median ROI: {df['roi'].median():.1f}%" if df["roi"].notna().any() else "- Median ROI: n/a",
    ]

    if best_genre is not None:
        lines.append(
            f"- Highest median ROI genre: {best_genre['genre']} ({best_genre['median_roi']:.1f}%, "
            f"{int(best_genre['film_count'])} films)"
        )
    if best_tier is not None:
        lines.append(f"- Best ROI budget tier: {best_tier['budget_tier']} ({best_tier['median_roi']:.1f}%)")

    lines.extend(["", "## Top Grossing Films"])
    for _, row in top_gross.iterrows():
        lines.append(f"- {row['name']} ({int(row['year'])}) - {format_money(row['gross_M'])}")

    lines.extend(["", "## Strongest Spearman Relationships"])
    for _, row in corr.iterrows():
        lines.append(f"- {row['Variable 1']} vs {row['Variable 2']}: {row['Spearman r']:.3f}")

    return "\n".join(lines)


def overview_page(df_raw: pd.DataFrame, df: pd.DataFrame) -> None:
    summary = summarize(df_raw, df)
    st.title("Movie Industry Intelligence")
    st.caption("Interactive reporting for the Kaggle movie industry dataset, adapted from the supplied notebook.")

    cols = st.columns(6)
    cols[0].metric("Raw rows", f"{summary.rows_raw:,}")
    cols[1].metric("Clean rows", f"{summary.rows_clean:,}")
    cols[2].metric("Financial rows", f"{summary.rows_financial:,}")
    cols[3].metric("Years", f"{summary.year_min}-{summary.year_max}")
    cols[4].metric("Genres", f"{summary.genre_count}")
    cols[5].metric("Countries", f"{summary.country_count}")

    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(yearly_trend(df), width="stretch")
    with right:
        st.plotly_chart(genre_count(df), width="stretch")

    st.subheader("Top performers")
    metric = st.radio(
        "Ranking metric",
        options=["gross_M", "profit_M", "roi", "score"],
        format_func=lambda x: {"gross_M": "Gross", "profit_M": "Profit", "roi": "ROI", "score": "Score"}[x],
        index=0,
        horizontal=True,
    )
    st.dataframe(top_movies(df, metric, 15), width="stretch", hide_index=True)


def eda_page(df: pd.DataFrame) -> None:
    st.title("Exploratory Analysis")
    cols = st.columns(4)
    cols[0].metric("Avg score", f"{df['score'].mean():.2f}")
    cols[1].metric("Median runtime", f"{df['runtime'].median():.0f} min")
    cols[2].metric("Median budget", format_money(df["budget_M"].median()))
    cols[3].metric("Median gross", format_money(df["gross_M"].median()))

    selected = st.selectbox(
        "Distribution",
        options=[
            ("score", "IMDb score"),
            ("budget_M", "Budget ($M)"),
            ("gross_M", "Gross ($M)"),
            ("runtime", "Runtime"),
        ],
        format_func=lambda item: item[1],
    )
    st.plotly_chart(distribution(df, selected[0], selected[1]), width="stretch")

    st.subheader("Outlier watchlist")
    outliers = df[df["iqr_outlier"]].sort_values("gross_M", ascending=False)
    st.dataframe(
        outliers[["name", "year", "genre", "score", "budget_M", "gross_M", "profit_M", "zscore_outlier"]].head(25),
        width="stretch",
        hide_index=True,
    )


def financial_page(df: pd.DataFrame) -> None:
    st.title("Financial Intelligence")
    min_films = st.slider("Minimum films per genre", 3, 75, 15)
    genre_stats = genre_financial_stats(df, min_films=min_films)
    tier_stats = budget_tier_stats(df)

    cols = st.columns(4)
    fin = financial_subset(df)
    cols[0].metric("Financial rows", f"{len(fin):,}")
    cols[1].metric("Median ROI", f"{fin['roi'].median():.1f}%" if not fin.empty else "n/a")
    cols[2].metric("Profitable films", f"{fin['profitable'].mean() * 100:.1f}%" if not fin.empty else "n/a")
    cols[3].metric("Avg profit", format_money(fin["profit_M"].mean()) if not fin.empty else "n/a")

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(genre_roi(genre_stats), width="stretch")
    with right:
        st.plotly_chart(budget_vs_gross(genre_stats), width="stretch")

    st.plotly_chart(tier_performance(tier_stats), width="stretch")
    st.plotly_chart(profit_vs_score(fin), width="stretch")

    with st.expander("Genre finance table", expanded=False):
        st.dataframe(genre_stats, width="stretch", hide_index=True)


def correlations_page(df: pd.DataFrame) -> None:
    st.title("Correlation Analysis")
    method = st.radio("Correlation method", ["spearman", "pearson"], horizontal=True)
    corr = df[NUMERIC_COLUMNS].dropna().corr(method=method)
    st.plotly_chart(correlation_heatmap(corr, f"{method.title()} correlation matrix"), width="stretch")

    st.subheader("Ranked relationships")
    st.dataframe(correlation_pairs(df, method), width="stretch", hide_index=True)

    st.info(
        "Spearman is usually more reliable here because movie budgets, grosses, and vote counts are heavily skewed."
    )


def explorer_page(df: pd.DataFrame) -> None:
    st.title("Data Explorer and Report")
    search = st.text_input("Search title, director, star, or company")
    view = df.copy()
    if search:
        text_cols = ["name", "director", "star", "company"]
        mask = False
        for col in text_cols:
            mask = mask | view[col].astype("string").str.contains(search, case=False, na=False)
        view = view[mask]

    cols_to_show = st.multiselect(
        "Columns",
        options=view.columns.tolist(),
        default=["name", "year", "rating", "genre", "score", "budget_M", "gross_M", "profit_M", "roi", "director", "star"],
    )
    st.dataframe(view[cols_to_show], width="stretch", hide_index=True)

    csv_bytes = view.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", csv_bytes, "filtered_movies.csv", "text/csv")

    report = build_markdown_report(df)
    st.download_button("Download markdown report", report, "movie_report.md", "text/markdown")
    with st.expander("Preview report", expanded=True):
        st.markdown(report)


def main() -> None:
    df_raw, df = get_data()
    filtered = apply_filters(df)

    st.sidebar.divider()
    st.sidebar.metric("Filtered movies", f"{len(filtered):,}")
    st.sidebar.metric("Average score", f"{filtered['score'].mean():.2f}" if not filtered.empty else "n/a")

    page = st.sidebar.radio(
        "Navigate",
        ["Overview", "Exploratory Analysis", "Financial Intelligence", "Correlations", "Data Explorer"],
    )

    if filtered.empty:
        st.warning("No movies match the current filters. Loosen one of the sidebar selections.")
        return

    if page == "Overview":
        overview_page(df_raw, filtered)
    elif page == "Exploratory Analysis":
        eda_page(filtered)
    elif page == "Financial Intelligence":
        financial_page(filtered)
    elif page == "Correlations":
        correlations_page(filtered)
    else:
        explorer_page(filtered)


if __name__ == "__main__":
    main()

