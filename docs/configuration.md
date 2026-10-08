# Configuration guide — model controls and test defaults

This guide explains the two Python configuration files. For how to run the
basic local test or one date with live market data, start with the root
`README.md`.

## `src/vanke_dtd/constants.py`

Use this file for stable policy and data-contract values: ticker symbols, source
URL, retry policy, QC thresholds, DTD calibration defaults and Excel column
names. Change it only when the underlying model or control policy changes, and
add/update a test for that change. It is version-controlled model and control
policy, not a day-to-day run form.

## `src/vanke_dtd/demo_settings.py`

Use this file for editable basic-test defaults: company number and the saved
replay date range. These are not financial-model settings. Command-line
arguments in `scripts/run_basic_test.py` override them for one basic-test run.
They do not limit the dates that an external user can process in LIVE mode.

## Basic test and live-run commands

| Choice | Basic local test | Live daily run |
|---|---|---|
| Command | `python scripts/run_basic_test.py` | `python scripts/run_daily.py --date YYYYMMDD` |
| Run mode | `REPLAY` | `LIVE` |
| Input source | Saved data in `data/replay/` and tracked controlled inputs | Yahoo Finance, HKMA API and tracked controlled inputs |
| Network call | Never | Yes |
| Write location | `runtime/demo_workspace/` | `runtime/live_workspace/` |
| Intended use | Confirm the local project works | Retrieve and process one date |

For either script, `--workspace` selects a different generated workspace and
`--keep` reuses one rather than resetting it.

## Do not store secrets here

The current public-source workflow has no required API key. If a future source
needs a credential, add its variable name to `.env.example`, keep the actual
`.env` ignored, and read it from the environment rather than committing it.
