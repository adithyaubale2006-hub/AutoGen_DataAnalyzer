from pathlib import Path

import pandas as pd

from src.helper import load_dataset


def load_and_profile(path: str | Path) -> tuple[pd.DataFrame, dict]:
	frame = load_dataset(path)
	return frame, {
		"rows": len(frame),
		"columns": len(frame.columns),
		"column_names": frame.columns.tolist(),
		"dtypes": {name: str(dtype) for name, dtype in frame.dtypes.items()},
		"missing_values": int(frame.isna().sum().sum()),
		"duplicates": int(frame.duplicated().sum()),
	}
