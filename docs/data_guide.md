# Data guide — standard inputs, basic-test fixture and generated results

## Standard daily-run inputs

| Location | File | Role | Write rule |
|---|---|---|---|
| `data/standard_inputs/confirmed_history/` | `vanke_confirmed_history.xlsx` | Confirmed Vanke Input and Output history through 2025-12-12 | Read-only baseline |
| `data/standard_inputs/confirmed_history/` | `vanke_historical_market_cap_reference.xlsx` | Historical market-cap reference supporting the baseline | Read-only reference |
| `data/standard_inputs/controlled_reference_data/` | `china_hk_trading_calendar.xlsx` | China/Hong Kong market-open controls through 2025-12-30 | Read-only during a run |
| `data/standard_inputs/controlled_reference_data/` | `vanke_effective_dated_company_data.xlsx` | Effective-dated shares and financial-statement fields | Add a reviewed effective-dated record only |
| `data/standard_inputs/controlled_reference_data/` | `hkma_364_day_bill_yield_cache.xlsx` | Local cache of 364-day HKMA bill yields | Copied to runtime before a live update |

## Basic-test fixture

`data/basic_test_fixture/vanke_market_data_20251213_to_20251219.xlsx` contains
saved market observations and QC evidence for the fixed basic local test. It is
not used by the live daily command and must remain read-only.

## Generated data

`runtime/` is local-only and ignored by Git. A workspace contains a copied
`vanke_confirmed_history.xlsx`, pending-review Input and Output, a market-data
audit and any Checker release result. Delete a runtime workspace to start a
clean run; do not delete or edit files in `data/` during normal operations.

## Test data

`tests/fixtures/` contains only small synthetic files/dataframes used to prove
specific rules. It is not the Vanke production-style dataset and must not be
used for financial interpretation.
