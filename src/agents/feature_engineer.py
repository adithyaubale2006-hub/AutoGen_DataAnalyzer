from pathlib import Path

import pandas as pd

from src.helper import engineer_features


def engineer_and_save(frame: pd.DataFrame, output_path: str | Path) -> tuple[pd.DataFrame, list[str]]:
	featured, created = engineer_features(frame)
	destination = Path(output_path)
	destination.parent.mkdir(parents=True, exist_ok=True)
	featured.to_csv(destination, index=False)
	return featured, created
