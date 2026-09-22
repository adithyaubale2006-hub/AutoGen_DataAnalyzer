from pathlib import Path

import pandas as pd

from src.config import OUTPUT_DIR
from src.helper import (
    build_report,
    clean_dataset,
    create_charts,
    engineer_features,
    load_dataset,
)


def run_pipeline(source: str | Path, output_dir: str | Path = OUTPUT_DIR) -> dict:
    """Run the deterministic portfolio workflow and persist its artifacts."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    frame = load_dataset(source)
    cleaned, cleaning = clean_dataset(frame)
    featured, features = engineer_features(cleaned)
    cleaned_path = destination / "cleaned_data.csv"
    feature_path = destination / "feature_engineered_data.csv"
    cleaned.to_csv(cleaned_path, index=False)
    featured.to_csv(feature_path, index=False)
    charts = create_charts(featured, destination)
    report = build_report(featured, cleaning, features, charts)
    report_path = destination / "final_report.md"
    report_path.write_text(report, encoding="utf-8")
    return {
        "source": frame,
        "cleaned": cleaned,
        "featured": featured,
        "cleaning": cleaning,
        "features": features,
        "charts": charts,
        "report": report,
        "artifacts": [cleaned_path, feature_path, report_path, *charts],
    }
