# Data guide — tracked and generated files

## Tracked source data

| Location | File | Role | Write rule |
|---|---|---|---|
| `data/baseline/` | `vanke.xlsx` | Supplied confirmed Input and Output history through 2025-12-12 | Read-only baseline |
| `data/baseline/` | `Daily_Calendar.xlsx` | Historical market-cap reference supporting the baseline | Read-only reference |
| `data/controlled/` | `China_HK_Trading_Calendar.xlsx` | China/Hong Kong market-open controls through 2025-12-30 | Read-only during a run |
| `data/controlled/` | `Vanke Issued Capital DataLog.xlsx` | Effective-dated shares and financial statement fields | Add a reviewed effective-dated record only |
| `data/controlled/` | `HKMA_Risk_Free_Daily.xlsx` | Local cache of 364-day HKMA bill yields | Copied to runtime before LIVE update |
| `data/replay/` | `Vanke_Daily_Datalog.xlsx` | Saved observations/QC evidence for deterministic REPLAY | Read-only replay fixture |

## Generated data

`runtime/` is local-only and ignored by Git. It contains copied working inputs,
Temporary Input, Temporary Output, the generated audit log and any Checker
release result. Delete a runtime workspace to start a clean run; do not delete
or edit files in `data/` during normal operations.

## Test data

`tests/fixtures/` contains only small synthetic files/dataframes used to prove
specific rules. It is not the Vanke production-style dataset and must not be
used for financial interpretation.
