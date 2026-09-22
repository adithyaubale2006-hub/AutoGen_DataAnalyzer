from pathlib import Path

import pandas as pd

from src.helper import clean_dataset


def clean_and_save(frame: pd.DataFrame, output_path: str | Path) -> tuple[pd.DataFrame, dict]:
	cleaned, metrics = clean_dataset(frame)
	destination = Path(output_path)
	destination.parent.mkdir(parents=True, exist_ok=True)
	cleaned.to_csv(destination, index=False)
	return cleaned, metrics
