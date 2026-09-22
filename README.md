# BondScope

BondScope is a Streamlit workspace for factual bond portfolio analysis. It loads a CSV, preserves the source, cleans duplicate and missing records, creates useful derived fields, generates portfolio charts, and writes a Markdown report.

## Run the dashboard

From the project root:

```powershell
streamlit run app.py
```

The included dataset is `data/bond_portfolio_data.csv`. You can upload another CSV from the sidebar. The dashboard stores generated artifacts in `outputs/`:

- `cleaned_data.csv`
- `feature_engineered_data.csv`
- `final_report.md`
- generated PNG charts

## Test the project

```powershell
python -m pytest -q
```

The reusable workflow is in `src/pipeline.py`; data operations and chart/report helpers are in `src/helper.py`. The agent modules are intentionally thin adapters, so the same logic can be called from a UI, tests, or a future AutoGen orchestration layer without making network calls.
