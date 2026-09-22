import pandas as pd

from src.execution.code_executor import execute_python
from src.helper import load_dataset
from src.pipeline import run_pipeline
import pytest


def test_execute_python_returns_stdout():
	result = execute_python("print('executor-ok')")

	assert result.returncode == 0
	assert result.stdout.strip() == "executor-ok"


def test_execute_python_returns_failure():
	result = execute_python("raise RuntimeError('expected failure')")

	assert result.returncode != 0
	assert "expected failure" in result.stderr


def test_pipeline_creates_expected_artifacts(tmp_path):
	source = tmp_path / "portfolio.csv"
	source.write_text("MarketValue_INR,Quantity,YieldToMaturity,CouponRate,Sector\n100,10,0.07,0.05,Public\n", encoding="utf-8")

	result = run_pipeline(source, tmp_path / "outputs")

	assert result["source"].shape == (1, 5)
	assert (tmp_path / "outputs" / "cleaned_data.csv").is_file()
	assert (tmp_path / "outputs" / "feature_engineered_data.csv").is_file()
	assert (tmp_path / "outputs" / "final_report.md").is_file()


def test_pipeline_accepts_generic_csv_schema(tmp_path):
	source = tmp_path / "sales.csv"
	source.write_text("customer,region,revenue\nA,North,100\nB,South,250\n", encoding="utf-8")

	result = run_pipeline(source, tmp_path / "generic_outputs")

	assert result["source"].shape == (2, 3)
	assert result["featured"]["revenue"].dtype.kind in "if"
	assert result["charts"]
	assert "revenue" in result["report"]


def test_load_dataset_rejects_empty_csv(tmp_path):
	source = tmp_path / "empty.csv"
	source.write_text("", encoding="utf-8")

	with pytest.raises((ValueError, pd.errors.EmptyDataError)):
		load_dataset(source)
