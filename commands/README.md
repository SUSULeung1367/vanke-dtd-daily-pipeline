# Commands — run the standard pipeline

Each command calls the shared implementation in
`src/vanke_dtd_pipeline/`; none contains its own DTD calculation.

| File | When to use it | What it does |
|---|---|---|
| `run_basic_pipeline_test.py` | First local check | Runs the fixed five-day offline test case. |
| `run_live_daily_pipeline.py` | Daily operation or scheduler | Retrieves live market data and runs one requested date. |
| `run_checker_daily_review.py` | After a pipeline run | Displays or records the Checker decision for one workspace. |
