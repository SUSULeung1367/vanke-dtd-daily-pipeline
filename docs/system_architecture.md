# System architecture — one standard pipeline, four ways to use it

## Core rule

`src/vanke_dtd_pipeline/` is the only standard implementation. The live daily
command, fixed basic test, demos and automated tests all call it. Demos and
tests do not contain a second copy of the DTD calculation.

## Standard-code modules

| Module | Responsibility |
|---|---|
| `pipeline_config.py` | Stable source, model, QC and schema settings. |
| `project_data_paths.py` | Locations of tracked standard inputs and the basic-test fixture. |
| `runtime_workspace.py` | Clear names for files generated in one isolated runtime workspace. |
| `market_data_sources.py` | Yahoo Finance, HKMA and the local risk-free-rate cache. |
| `daily_input_checks.py` | Source-date, plausibility and day-on-day checks. |
| `daily_input_builder.py` | Build one daily DTD Input and its audit record. |
| `runtime_file_store.py` | Write pending-review Input and market-data audit files. |
| `daily_dtd_calculator.py` | Trading-day sequence, asset-value estimation and DTD calculation. |
| `daily_result_reviewer.py` | Checker table, approval/rejection and append-only release. |
| `daily_pipeline_runner.py` | The shared end-to-end runner used by every run mode. |

## Run profiles

| Profile | Command | Input source | Purpose |
|---|---|---|---|
| Basic test | `commands/run_basic_pipeline_test.py` | `data/basic_test_fixture/` | Verify the local installation with fixed dates. |
| Live daily run | `commands/run_live_daily_pipeline.py --date YYYYMMDD` | Yahoo Finance, HKMA and `data/standard_inputs/` | Run one daily market-data update. |
| Demo | `demos/*.ipynb` | The standard runner and isolated workspace | Explain the pipeline to a reviewer. |
| Automated test | `pytest` | Fixed fixture and small test data | Prevent code regressions. |

## Runtime flow

`data/` → isolated `runtime/<workspace>/` → daily Input build and checks →
pending-review Input → DTD calculation → pending-review Output → Checker or
Marker review → append-only confirmed history inside that runtime workspace.

Tracked files in `data/` are never modified by normal runs.
