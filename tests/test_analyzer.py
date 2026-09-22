import pandas as pd

from src.helper import summarize


def test_summarize_reports_portfolio_metrics():
	frame = pd.DataFrame({"MarketValue_INR": [100, 250], "ModifiedDuration": [2.0, 4.0], "Sector": ["A", "B"]})

	result = summarize(frame)

	assert result["rows"] == 2
	assert result["columns"] == 3
	assert result["total_market_value"] == 350.0
	assert result["average_duration"] == 3.0


def test_summarize_counts_missing_and_duplicates():
	frame = pd.DataFrame({"value": [1, 1, None]})

	result = summarize(frame)

	assert result["missing"] == 1
	assert result["duplicates"] == 1
