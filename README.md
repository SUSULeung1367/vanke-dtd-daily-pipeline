# Vanke Daily DTD Pipeline

A reviewable daily Vanke Distance-to-Default (DTD) pipeline. There is one
standard implementation in `src/vanke_dtd_pipeline/`. The live daily command,
basic local test, interactive demos and automated tests all call that same
implementation; none contains a second DTD calculation.

## Why DTD matters

DTD is a structural credit-risk valuation signal. It combines the market's
daily pricing of Vanke equity with liabilities and the risk-free rate to infer
an unobserved market value of assets and measure its buffer above the firm's
default point. This provides an additional way to monitor how daily
market-price movements are reflected in the firm's implied credit condition.
It complements, rather than replaces, observation of the share price itself.

DTD is not a fair-value estimate for the share price and is not investment
advice. This repository is a reviewable demonstration template for a
production-style monitoring workflow, not a deployed production service.

## What this pipeline does

1. Prepares the daily Vanke DTD input from market prices, CNY/HKD FX,
   effective-dated company information and the HKMA bill yield.
2. Calculates a daily provisional DTD for the next eligible Hong Kong trading
   date.
3. Checks source dates, plausibility and day-on-day movements before a result
   can be reviewed.

## Start here

| Your goal | Use this |
|---|---|
| Check that the project works on your computer | `python commands/run_basic_pipeline_test.py` |
| Run the daily pipeline with live market data | `python commands/run_live_daily_pipeline.py --date YYYYMMDD` |
| Review or approve daily results | `python commands/run_checker_daily_review.py` |
| Understand the standard code | [`docs/system_architecture.md`](docs/system_architecture.md) |
| Understand the input files | [`docs/data_guide.md`](docs/data_guide.md) |
| Understand Checker and Marker | [`docs/daily_review_guide.md`](docs/daily_review_guide.md) |

## Environment setup

Use Python 3.11 to 3.13. The commands below use a local virtual environment so
the project dependencies do not affect other Python projects.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The installation makes the `src/vanke_dtd_pipeline` package available and installs
`pytest` for the test suite.

## 1. Basic local test

```powershell
python commands/run_basic_pipeline_test.py
```

This is the first command for a new user or reviewer. It calls the standard
pipeline with the fixed basic-test period 2025-12-13 to 2025-12-19 and verifies
the local environment, data contract, trading-day rules and DTD flow. It does
not call Yahoo Finance or the HKMA API.

Expected result:

- 2025-12-13 and 2025-12-14 are reported as Hong Kong-closed dates.
- 2025-12-15 through 2025-12-19 create five sequential provisional DTD rows.
- All generated files are written below `runtime/basic_test_workspace/`.
- `data/` remains unchanged.

To choose another supported basic-test interval or retain the current workspace:

```powershell
python commands/run_basic_pipeline_test.py --start 20251213 --end 20251219 --keep
```

## 2. Daily data review: Checker and Marker

**Checker** is the daily reviewer. The Checker approves or rejects a normal
result after automated checks and a provisional DTD are available.

**Marker** handles warnings, data exceptions and manual changes. These are not
normal daily approvals; they need Marker review and an audit record.

To display the daily review table without writing anything, run:

```powershell
python commands/run_checker_daily_review.py
```

After reviewing, an explicit decision can be recorded in the generated
workspace. For example:

```powershell
python commands/run_checker_daily_review.py --decision APPROVE --checker "Reviewer Name" --dates 20251215 20251216
```

Approval is intentionally limited to normal rows with passing automated QC,
a provisional DTD and no Marker requirement. The confirmed history in
`data/standard_inputs/` is never changed; any release affects only that runtime
workspace.

## 3. Live daily pipeline

```powershell
python commands/run_live_daily_pipeline.py --date 20251215
```

This command calls the same standard pipeline with live sources: Yahoo Finance
provides Vanke A/H closes and CNY/HKD FX; the HKMA API provides the risk-free
rate. It writes results only to `runtime/live_daily_workspace/` unless you pass
`--workspace`.

To run it automatically each day, configure a scheduler to call this command
with the required date after the market-data cut-off. The repository provides
the daily command; scheduling stays outside the code so it can run locally or
in another environment.

## 4. Demos

The notebooks demonstrate the standard code; they never reproduce the DTD
calculation.

| Demo | Purpose |
|---|---|
| `demos/01_daily_pipeline_demo.ipynb` | Run the basic daily pipeline flow and inspect outputs. |
| `demos/02_daily_review_demo.ipynb` | Inspect the Checker table and record a decision. |
| `demos/03_dtd_trading_day_sequence_demo.ipynb` | Show why DTD dates must follow the Hong Kong trading-day sequence. |

## 5. Automated tests

```powershell
pytest
```

The tests check the basic pipeline run, trading-calendar rules and project file
layout. They use the fixed basic-test fixture and never make a LIVE network
request.

## Repository map

```text
src/vanke_dtd_pipeline/       Standard shared Python implementation
commands/                     Commands a user or scheduler runs
demos/                        Ordered notebooks that demonstrate the standard code
tests/                        Automated checks of the standard code
data/standard_inputs/         Confirmed history and controlled daily-run inputs
data/basic_test_fixture/      Fixed market data for the basic local test only
runtime/                      Generated local results; ignored by Git
docs/                         Short guides for reviewers and users
archive/                      Earlier versions retained only for reference
```

## Public Python API

```python
from vanke_dtd_pipeline.daily_pipeline_runner import run_date_range
from vanke_dtd_pipeline.checker_daily_result_reviewer import build_checker_table

result = run_date_range("20251213", "20251219", mode="BASIC_TEST")
review = build_checker_table(result.workspace)
```

See [`docs/system_architecture.md`](docs/system_architecture.md) for each
standard-code module and [`docs/configuration_guide.md`](docs/configuration_guide.md)
for settings that are safe to change.
