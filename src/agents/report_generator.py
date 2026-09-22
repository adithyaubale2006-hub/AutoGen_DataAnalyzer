from pathlib import Path

import pandas as pd

from src.helper import build_report


def generate_report(frame: pd.DataFrame, cleaning: dict, features: list[str], charts: list[Path], output_path: str | Path) -> Path:
	destination = Path(output_path)
	destination.parent.mkdir(parents=True, exist_ok=True)
	destination.write_text(build_report(frame, cleaning, features, charts), encoding="utf-8")
	return destination
