from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load a CSV and provide a useful error for missing or empty inputs."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Dataset not found: {source}")
    frame = pd.read_csv(source)
    if frame.empty:
        raise ValueError(f"Dataset is empty: {source}")
    return frame


def clean_dataset(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    cleaned = frame.drop_duplicates().copy()
    missing_before = int(frame.isna().sum().sum())
    
    for column in cleaned.columns:
        if not (pd.api.types.is_object_dtype(cleaned[column]) or pd.api.types.is_string_dtype(cleaned[column])):
            continue
        converted = pd.to_numeric(cleaned[column], errors="coerce")
        if converted.notna().sum() >= max(1, int(len(cleaned) * 0.8)):
            cleaned[column] = converted
            
    for column in cleaned.select_dtypes(include="number"):
        if cleaned[column].isna().any():
            median = cleaned[column].median()
            cleaned[column] = cleaned[column].fillna(0 if pd.isna(median) else median)
            
    for column in cleaned.select_dtypes(exclude="number"):
        if cleaned[column].isna().any():
            cleaned[column] = cleaned[column].fillna("Unknown")
            
    return cleaned, {
        "rows_before": len(frame),
        "rows_after": len(cleaned),
        "duplicates_removed": len(frame) - len(cleaned),
        "missing_values": missing_before,
    }


def engineer_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    result = frame.copy()
    created: list[str] = []
    
    if {"MarketValue_INR", "Quantity"}.issubset(result.columns):
        result["MarketValuePerUnit"] = result["MarketValue_INR"].div(result["Quantity"].replace(0, pd.NA))
        created.append("MarketValuePerUnit")
        
    if {"YieldToMaturity", "CouponRate"}.issubset(result.columns):
        result["YieldMinusCoupon"] = result["YieldToMaturity"] - result["CouponRate"]
        created.append("YieldMinusCoupon")
        
    return result, created


def analytical_numeric_columns(frame: pd.DataFrame) -> list[str]:
    """Return numeric measures while avoiding identifier columns in charts and KPIs."""
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    measures = [
        column for column in numeric_columns
        if not column.lower().endswith("id")
    ]
    return measures or numeric_columns


def summarize(frame: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = analytical_numeric_columns(frame)
    summary: dict[str, Any] = {
        "rows": len(frame),
        "columns": len(frame.columns),
        "missing": int(frame.isna().sum().sum()),
        "duplicates": int(frame.duplicated().sum()),
        "numeric_columns": len(numeric_columns),
    }
    
    if "MarketValue_INR" in frame:
        summary["total_market_value"] = float(frame["MarketValue_INR"].sum())
    if "ModifiedDuration" in frame:
        summary["average_duration"] = float(frame["ModifiedDuration"].mean())
        
    if numeric_columns:
        primary = numeric_columns[0]
        summary["primary_numeric_column"] = primary
        summary["primary_numeric_total"] = float(frame[primary].sum())
        summary["primary_numeric_mean"] = float(frame[primary].mean())
        
    return summary


def create_charts(frame: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    
    for stale_name in {
        "yield_distribution.png",
        "market_value_by_sector.png",
        "market_value_by_rating.png",
        "duration_vs_yield.png",
        "numeric_distribution.png",
        "numeric_by_category.png",
        "category_counts.png",
        "numeric_relationship.png",
        "correlation_heatmap.png",
    }:
        stale_path = destination / stale_name
        if stale_path.exists():
            stale_path.unlink()
            
    numeric_columns = analytical_numeric_columns(frame)
    categorical_columns = frame.select_dtypes(exclude="number").columns.tolist()
    
    plt.rcParams.update({
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": "#b7c2bc",
        "axes.grid": True,
        "grid.color": "#e5ebe6",
        "grid.linewidth": 0.8,
        "font.size": 10,
    })

    def save_chart(fig: plt.Figure, filename: str) -> None:
        path = destination / filename
        fig.tight_layout()
        fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        paths.append(path)

    if numeric_columns:
        column = "YieldToMaturity" if "YieldToMaturity" in frame else numeric_columns[0]
        values = frame[column].dropna()
        if not values.empty:
            fig, axis = plt.subplots(figsize=(8, 4.5), facecolor="white")
            axis.hist(values, bins=min(20, max(5, values.nunique())), color="#d97757", edgecolor="white", alpha=0.9)
            axis.axvline(values.mean(), color="#192b35", linestyle="--", linewidth=1.4, label=f"Mean {values.mean():,.2f}")
            axis.set(title=f"{column} distribution", xlabel=column, ylabel="Records")
            axis.legend(frameon=False)
            save_chart(fig, "numeric_distribution.png")

    if categorical_columns and numeric_columns:
        category = categorical_columns[0]
        value = "MarketValue_INR" if "MarketValue_INR" in frame else numeric_columns[0]
        values = frame.assign(_category=frame[category].astype(str)).groupby("_category")[value].sum().sort_values().tail(12)
        fig, axis = plt.subplots(figsize=(8, 4.5), facecolor="white")
        axis.barh(values.index, values.values, color="#2c6e70")
        axis.set(title=f"{value} by {category}", xlabel=value, ylabel=category)
        axis.spines[["top", "right"]].set_visible(False)
        save_chart(fig, "numeric_by_category.png")
    elif categorical_columns:
        category = categorical_columns[0]
        counts = frame[category].astype(str).value_counts().head(12).sort_values()
        fig, axis = plt.subplots(figsize=(8, 4.5), facecolor="white")
        axis.barh(counts.index, counts.values, color="#2c6e70")
        axis.set(title=f"Records by {category}", xlabel="Records", ylabel=category)
        axis.spines[["top", "right"]].set_visible(False)
        save_chart(fig, "category_counts.png")

    if len(numeric_columns) >= 2:
        left, right = numeric_columns[:2]
        plot_frame = frame[[left, right]].dropna()
        if len(plot_frame) >= 2:
            fig, axis = plt.subplots(figsize=(8, 4.5), facecolor="white")
            axis.scatter(plot_frame[left], plot_frame[right], s=34, alpha=0.7, color="#a9822f", edgecolors="white", linewidths=0.5)
            axis.set(title=f"{right} versus {left}", xlabel=left, ylabel=right)
            axis.spines[["top", "right"]].set_visible(False)
            save_chart(fig, "numeric_relationship.png")

    if len(numeric_columns) >= 3:
        correlation = frame[numeric_columns[:10]].corr()
        fig, axis = plt.subplots(figsize=(8, 6), facecolor="white")
        image = axis.imshow(correlation, cmap="RdYlBu_r", vmin=-1, vmax=1)
        axis.set_xticks(range(len(correlation)), correlation.columns, rotation=45, ha="right")
        axis.set_yticks(range(len(correlation)), correlation.index)
        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04, label="Correlation")
        axis.set_title("Numeric feature correlations")
        save_chart(fig, "correlation_heatmap.png")
        
    return paths


def build_report(frame: pd.DataFrame, cleaning: dict[str, Any], features: list[str], chart_paths: list[Path]) -> str:
    stats = summarize(frame)
    feature_lines = [f"- `{name}`" for name in features] or ["- No derived features were required."]
    chart_lines = [f"- `{path.name}`" for path in chart_paths] or ["- No charts were generated."]
    lines = [
        "# Data Analysis Report",
        "",
        "## Executive Summary",
        f"The dataset contains **{stats['rows']} records** and **{stats['columns']} columns**.",
        f"Primary numeric measure: **{stats.get('primary_numeric_column', 'Not available')}**.",
        f"Primary numeric total: **{stats.get('primary_numeric_total', 0):,.2f}**.",
        "",
        "## Data Quality",
        f"- Missing values before cleaning: {cleaning['missing_values']}",
        f"- Duplicate rows removed: {cleaning['duplicates_removed']}",
        f"- Rows after cleaning: {cleaning['rows_after']}",
        "",
        "## Feature Engineering",
        *feature_lines,
        "",
        "## Key Metrics",
        f"- Primary numeric average: {stats.get('primary_numeric_mean', 0):,.4f}",
        f"- Numeric columns: {stats['numeric_columns']}",
        "",
        "## Visualizations",
        *chart_lines,
    ]
    return "\n".join(lines) + "\n"


@dataclass
class AnalysisState:
    """Optional lightweight run-state tracker, not currently wired into run_pipeline().

    Nothing else in this module reads or writes an AnalysisState yet — it's kept
    here in case pipeline.py (or a future caller) wants a structured way to track
    a run's status, errors, and produced artifacts across multiple steps.
    """

    source_path: Path
    output_dir: Path
    status: str = "ready"
    errors: list[str] = field(default_factory=list)
    artifacts: dict[str, Path] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.status = "failed"
        self.errors.append(message)

    def complete(self) -> None:
        self.status = "complete"