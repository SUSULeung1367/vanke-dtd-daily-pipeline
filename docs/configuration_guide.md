# Configuration guide — safe settings and run commands

## Standard pipeline configuration

`src/vanke_dtd_pipeline/pipeline_config.py` contains stable settings shared by
every mode: ticker symbols, source URL, retry policy, QC thresholds, DTD
defaults and Excel column names. Change it only when the model or control
policy changes, and add or update a test at the same time.

The fixed dates for the basic test are intentionally not stored in the standard
package. They are named directly in `commands/run_basic_pipeline_test.py`, so a
reader can see they belong only to that test command.

## Commands

| Command | What it does | Data source | Default workspace |
|---|---|---|---|
| `python commands/run_basic_pipeline_test.py` | Checks that the standard pipeline works locally for the known five-day case. | `data/basic_test_fixture/` | `runtime/basic_test_workspace/` |
| `python commands/run_live_daily_pipeline.py --date YYYYMMDD` | Runs the standard daily pipeline for one requested date. | Yahoo Finance, HKMA and `data/standard_inputs/` | `runtime/live_daily_workspace/` |
| `python commands/run_daily_review.py` | Shows or records Checker decisions for a workspace. | Generated runtime files | `runtime/basic_test_workspace/` |

For any command, `--workspace` selects a different generated workspace and
`--keep` reuses it rather than resetting it.

## Do not store secrets here

The current public-source workflow has no required API key. If a future source
needs a credential, add its variable name to `.env.example`, keep the actual
`.env` ignored, and read it from the environment rather than committing it.
