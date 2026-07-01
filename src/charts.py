from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CHART_TEMPLATE = "plotly_white"
BLUE = "#2563eb"
TEAL = "#0f766e"
AMBER = "#d97706"
ROSE = "#be123c"
INK = "#111827"


def apply_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        title_font=dict(size=18, color=INK),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white"),
    )
    return fig


def yearly_trend(df: pd.DataFrame) -> go.Figure:
    yearly = (
        df.groupby("year")
        .agg(
            films=("name", "count"),
            avg_score=("score", "mean"),
            median_gross_M=("gross_M", "median"),
        )
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(x=yearly["year"], y=yearly["films"], name="Films", marker_color=BLUE))
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["avg_score"],
            name="Avg score",
            yaxis="y2",
            line=dict(color=AMBER, width=3),
        )
    )
    fig.update_layout(
        title="Movie volume and average score by year",
        yaxis=dict(title="Films"),
        yaxis2=dict(title="Avg score", overlaying="y", side="right", range=[0, 10]),
    )
    return apply_layout(fig)


def genre_count(df: pd.DataFrame) -> go.Figure:
    counts = df["genre"].value_counts().head(15).reset_index()
    counts.columns = ["genre", "films"]
    fig = px.bar(counts, x="films", y="genre", orientation="h", title="Most common genres", color_discrete_sequence=[TEAL])
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    return apply_layout(fig)


def distribution(df: pd.DataFrame, column: str, label: str) -> go.Figure:
    fig = px.histogram(
        df.dropna(subset=[column]),
        x=column,
        nbins=45,
        marginal="box",
        title=f"Distribution of {label}",
        color_discrete_sequence=[BLUE],
    )
    return apply_layout(fig)


def genre_roi(stats: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        stats.sort_values("median_roi", ascending=True),
        x="median_roi",
        y="genre",
        orientation="h",
        color="pct_profitable",
        color_continuous_scale=["#fee2e2", "#f59e0b", "#0f766e"],
        title="Genre ROI ranking",
        hover_data=["film_count", "avg_budget_M", "avg_gross_M", "avg_profit_M"],
    )
    fig.update_xaxes(title="Median ROI (%)")
    return apply_layout(fig, height=520)


def budget_vs_gross(stats: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        stats,
        x="avg_budget_M",
        y="avg_gross_M",
        size="film_count",
        color="median_roi",
        text="genre",
        color_continuous_scale=["#be123c", "#d97706", "#0f766e"],
        title="Average budget vs gross by genre",
        hover_data=["pct_profitable", "avg_profit_M"],
    )
    fig.update_traces(textposition="top center")
    fig.update_xaxes(title="Average budget ($M)")
    fig.update_yaxes(title="Average gross ($M)")
    return apply_layout(fig, height=520)


def tier_performance(stats: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=stats["budget_tier"], y=stats["avg_gross_M"], name="Avg gross", marker_color=BLUE))
    fig.add_trace(go.Bar(x=stats["budget_tier"], y=stats["avg_profit_M"], name="Avg profit", marker_color=TEAL))
    fig.update_layout(title="Budget tier performance", barmode="group", yaxis_title="$M")
    return apply_layout(fig)


def profit_vs_score(df: pd.DataFrame) -> go.Figure:
    sample = df.dropna(subset=["score", "profit_M", "budget_tier"]).copy()
    if len(sample) > 2500:
        sample = sample.sample(2500, random_state=42)
    fig = px.scatter(
        sample,
        x="score",
        y="profit_M",
        color="budget_tier",
        size="gross_M",
        hover_name="name",
        hover_data=["year", "genre", "budget_M", "gross_M"],
        title="Profit vs IMDb score",
    )
    fig.update_xaxes(title="IMDb score")
    fig.update_yaxes(title="Profit ($M)")
    return apply_layout(fig, height=520)


def correlation_heatmap(corr: pd.DataFrame, title: str) -> go.Figure:
    fig = px.imshow(
        corr,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale=["#be123c", "#ffffff", "#0f766e"],
        title=title,
    )
    return apply_layout(fig, height=520)
