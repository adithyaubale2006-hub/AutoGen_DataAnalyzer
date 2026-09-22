from pathlib import Path

import pandas as pd

from src.helper import create_charts


def visualize(frame: pd.DataFrame, output_dir: str | Path) -> list[Path]:
	return create_charts(frame, output_dir)
