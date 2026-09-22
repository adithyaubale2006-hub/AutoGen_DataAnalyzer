import pandas as pd
import pytest

from src.helper import clean_dataset, engineer_features


def test_clean_dataset_removes_duplicates_and_fills_values():
	frame = pd.DataFrame({"amount": [10.0, None, 10.0], "sector": ["A", "B", "A"]})
	cleaned, metrics = clean_dataset(frame)

	assert len(cleaned) == 2
	assert cleaned["amount"].isna().sum() == 0
	assert metrics["duplicates_removed"] == 1
	assert frame.isna().sum().sum() == 1


def test_engineer_features_handles_zero_quantity():
	frame = pd.DataFrame({"MarketValue_INR": [100.0], "Quantity": [0], "YieldToMaturity": [0.07], "CouponRate": [0.05]})
	featured, created = engineer_features(frame)

	assert created == ["MarketValuePerUnit", "YieldMinusCoupon"]
	assert pd.isna(featured.loc[0, "MarketValuePerUnit"])
	assert featured.loc[0, "YieldMinusCoupon"] == pytest.approx(0.02)
