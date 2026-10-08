# Vanke Daily DTD Pipeline

A reviewable, replayable, production-oriented data-engineering monitoring
template for a daily China Vanke Distance-to-Default (DTD) workflow. The
repository separates market-data preparation, quality control, DTD calculation
and human release. It demonstrates how an incremental daily pipeline can be
inspected, replayed and tested without overwriting confirmed history.

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

| If you want to... | Read or run... |
|---|---|
| Understand the architecture | [`docs/architecture.md`](docs/architecture.md) |
| Understand every tracked dataset | [`docs/data_dictionary.md`](docs/data_dictionary.md) |
| Understand configuration | [`docs/configuration.md`](docs/configuration.md) |
| Understand the Checker/Marker rule | [`docs/governance.md`](docs/governance.md) |
| Check that the project works locally | `python scripts/run_basic_test.py` |
| Inspect or apply a Checker decision | `python scripts/run_checker.py` |
| Run one date with live market data | `python scripts/run_daily.py --date YYYYMMDD` |

## Environment setup

Use Python 3.11 to 3.13. The commands below use a local virtual environment so
the project dependencies do not affect other Python projects.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The installation makes the `src/vanke_dtd` package available and installs
`pytest` for the test suite.

## Run the basic local test

```powershell
python scripts/run_basic_test.py
```

This test verifies the local environment and the full pipeline flow. Expected
result:

- 2025-12-13 and 2025-12-14 are reported as Hong Kong-closed dates.
- 2025-12-15 through 2025-12-19 create five sequential provisional DTD rows.
- All generated files are written below `runtime/demo_workspace/`.
- `data/` remains unchanged.

To choose another supported replay interval or retain the current workspace:

```powershell
python scripts/run_basic_test.py --start 20251213 --end 20251219 --keep
```

## Daily data review: Checker and Marker

**Checker** is the daily reviewer. The Checker approves or rejects a normal
result after automated checks and a provisional DTD are available.

**Marker** handles warnings, data exceptions and manual changes. These are not
normal daily approvals; they need Marker review and an audit record.

To display the daily review table without writing anything, run:

```powershell
python scripts/run_checker.py
```

After reviewing, an explicit decision can be recorded in the generated
workspace. For example:

```powershell
python scripts/run_checker.py --decision APPROVE --checker "Reviewer Name" --dates 20251215 20251216
```

Approval is intentionally limited to normal rows with passing automated QC,
a provisional DTD and no Marker requirement. The baseline file in
`data/baseline/` is never changed; any release affects only that runtime
workspace.

## Run with live market data

```powershell
python scripts/run_daily.py --date 20251215
```

This command retrieves Yahoo Finance Vanke A/H closes and CNY/HKD FX, and the
HKMA risk-free rate, then runs the same validation and provisional DTD
calculation. Use a date covered by the controlled calendar. Source/API failure
and source-date mismatches are recorded and blocked from the review flow.

## Run tests

```powershell
pytest
```

The tests focus on data contracts, calendar gating, sequential DTD processing
and append-only release rules. They use local inputs and must not make a LIVE
network request.

## Repository map

```text
src/vanke_dtd/   Canonical callable Python implementation
scripts/         Simple daily, replay and Checker entry points
notebooks/       Thin demonstrations that call the package
tests/           Automated unit/integration tests and small fixtures
data/            Tracked baseline, controlled and replay inputs
docs/            Reviewer documentation and reference materials
runtime/         Generated local workspaces only; ignored by Git
archive/         Earlier notebooks, documents and out-of-scope analysis
```

## Public Python API

```python
from vanke_dtd.workflow import run_date_range
from vanke_dtd.checker import build_checker_table, confirm_dates

result = run_date_range("20251213", "20251219", mode="REPLAY")
review = build_checker_table(result.workspace)
```

For layer-level review, use `vanke_dtd.ingestion`, `vanke_dtd.quality`,
`vanke_dtd.sources`, `vanke_dtd.dtd`, `vanke_dtd.store` and
`vanke_dtd.checker`. Each layer's responsibility is documented in
[`docs/architecture.md`](docs/architecture.md).
