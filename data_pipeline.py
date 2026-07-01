from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


NUMERIC_COLUMNS = ["score", "votes", "budget", "gross", "runtime", "year"]


@dataclass(frozen=True)
class DatasetSummary:
    rows_raw: int
    rows_clean: int
    rows_financial: int
    year_min: int
    year_max: int
    genre_count: int
    country_count: int


def load_movies(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_movies(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df = df.dropna(subset=["name", "genre", "year", "score", "runtime"])
    df = df.drop_duplicates()

    for col in ["budget", "gross", "votes", "score", "runtime", "year"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    released_parts = df["released"].astype("string").str.split(r" \(", n=1, expand=True)
    df["released_date_text"] = released_parts[0]
    if released_parts.shape[1] > 1:
        df["country_release"] = released_parts[1].str.replace(")", "", regex=False)
    else:
        df["country_release"] = pd.NA
    df["released_date"] = pd.to_datetime(df["released_date_text"], errors="coerce")

    df["budget_M"] = df["budget"] / 1_000_000
    df["gross_M"] = df["gross"] / 1_000_000
    df["profit"] = df["gross"] - df["budget"]
    df["profit_M"] = df["profit"] / 1_000_000
    df["roi"] = np.where(
        (df["budget"].notna()) & (df["budget"] > 0),
        (df["profit"] / df["budget"]) * 100,
        np.nan,
    )
    df["profitable"] = df["profit"] > 0

    financial_mask = df["budget"].notna() & df["gross"].notna() & (df["budget"] > 0)
    df.loc[financial_mask, "budget_tier"] = pd.qcut(
        df.loc[financial_mask, "budget"],
        q=4,
        labels=["Low", "Medium", "High", "Blockbuster"],
        duplicates="drop",
    ).astype("string")
    df["budget_tier"] = df["budget_tier"].fillna("Unknown")

    df["decade"] = (df["year"] // 10 * 10).astype("Int64").astype("string") + "s"
    df = add_outlier_flags(df)
    return df


def add_outlier_flags(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    iqr_flags = pd.Series(False, index=result.index)
    zscore_flags = pd.Series(False, index=result.index)

    for col in ["budget_M", "gross_M", "score"]:
        values = result[col].dropna()
        if values.empty:
            continue

        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr > 0:
            iqr_flags.loc[values.index] |= (values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)

        std = values.std(ddof=0)
        if std > 0:
            z = (values - values.mean()) / std
            zscore_flags.loc[values.index] |= z.abs() > 3

    result["iqr_outlier"] = iqr_flags
    result["zscore_outlier"] = zscore_flags
    return result


def summarize(df_raw: pd.DataFrame, df: pd.DataFrame) -> DatasetSummary:
    financial = financial_subset(df)
    return DatasetSummary(
        rows_raw=len(df_raw),
        rows_clean=len(df),
        rows_financial=len(financial),
        year_min=int(df["year"].min()),
        year_max=int(df["year"].max()),
        genre_count=int(df["genre"].nunique()),
        country_count=int(df["country"].nunique()),
    )


def financial_subset(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["budget"].notna() & df["gross"].notna() & (df["budget"] > 0)].copy()


def genre_financial_stats(df: pd.DataFrame, min_films: int = 15) -> pd.DataFrame:
    fin = financial_subset(df)
    stats = (
        fin.groupby("genre", dropna=False)
        .agg(
            film_count=("gross", "count"),
            median_roi=("roi", "median"),
            avg_budget_M=("budget_M", "mean"),
            avg_gross_M=("gross_M", "mean"),
            avg_profit_M=("profit_M", "mean"),
            pct_profitable=("profitable", lambda s: s.mean() * 100),
            avg_score=("score", "mean"),
        )
        .reset_index()
    )
    return stats[stats["film_count"] >= min_films].sort_values("median_roi", ascending=False)


def budget_tier_stats(df: pd.DataFrame) -> pd.DataFrame:
    fin = financial_subset(df)
    order = ["Low", "Medium", "High", "Blockbuster"]
    stats = (
        fin[fin["budget_tier"].isin(order)]
        .groupby("budget_tier", observed=True)
        .agg(
            film_count=("gross", "count"),
            avg_budget_M=("budget_M", "mean"),
            avg_gross_M=("gross_M", "mean"),
            avg_profit_M=("profit_M", "mean"),
            median_roi=("roi", "median"),
            pct_profitable=("profitable", lambda s: s.mean() * 100),
            avg_score=("score", "mean"),
        )
        .reindex(order)
        .reset_index()
    )
    return stats


def correlation_pairs(df: pd.DataFrame, method: str = "spearman") -> pd.DataFrame:
    cols = [col for col in NUMERIC_COLUMNS if col in df.columns]
    corr = df[cols].dropna().corr(method=method)
    pairs = (
        corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        .stack()
        .reset_index()
    )
    pairs.columns = ["Variable 1", "Variable 2", f"{method.title()} r"]
    return pairs.reindex(pairs[f"{method.title()} r"].abs().sort_values(ascending=False).index)


def top_movies(df: pd.DataFrame, metric: str, n: int = 10) -> pd.DataFrame:
    columns = ["name", "year", "genre", "score", "budget_M", "gross_M", "profit_M", "roi", "director", "star"]
    available = [col for col in columns if col in df.columns]
    return df.dropna(subset=[metric]).nlargest(n, metric)[available].reset_index(drop=True)
