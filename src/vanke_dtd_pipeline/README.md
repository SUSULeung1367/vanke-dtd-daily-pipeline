# Standard pipeline code — shared by every run mode

This package is the single source of DTD calculation and daily-processing
logic. Commands, demos and pytest tests call these modules; they do not copy
their logic elsewhere.

| Module | Responsibility |
|---|---|
| `pipeline_config.py` | Stable model, source, quality-control and schema settings. |
| `project_data_paths.py` | Paths to standard daily inputs and the basic-test fixture. |
| `runtime_workspace.py` | Names and locations for one generated runtime workspace. |
| `market_data_sources.py` | Yahoo Finance, HKMA and cached risk-free-rate retrieval. |
| `daily_input_checks.py` | Source-date, plausibility and day-on-day input checks. |
| `daily_input_builder.py` | Builds one pending-review daily DTD Input and audit record. |
| `runtime_file_store.py` | Writes generated Input and audit Excel files. |
| `daily_dtd_calculator.py` | Enforces trading-day continuity and calculates DTD. |
| `checker_daily_result_reviewer.py` | Builds the Checker review table and records normal approvals/rejections. |
| `daily_pipeline_runner.py` | Runs the complete standard pipeline in `BASIC_TEST` or `LIVE` mode. |
