import pandas as pd

from src.helper import summarize


def analyze(frame: pd.DataFrame) -> dict:
	return summarize(frame)
