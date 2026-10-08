# System architecture — modules and data flow

## Design rule

There is one canonical implementation: `src/vanke_dtd/`. Notebooks and
scripts call that package; they do not reproduce its financial calculations.

## Layers

| Layer | Main files | Responsibility |
|---|---|---|
| Configuration | `constants.py`, `demo_settings.py` | Model policy and editable demo defaults |
| Source access | `sources.py` | Yahoo Finance, HKMA and local rate cache |
| Input controls | `quality.py`, `store.py`, `ingestion.py` | QC, Temporary Input and audit log |
| DTD engine | `dtd.py` | Calendar sequence, Merton inversion and DTD output |
| Release control | `checker.py` | Checker table, approval/rejection and append-only release |
| Workflow | `workflow.py` | Safe end-to-end range orchestration |

## Runtime flow

`data/` → isolated `runtime/<workspace>/` → input preparation and QC →
Temporary Input → DTD calculation → Temporary Output → Checker review →
append-only confirmed history inside that runtime workspace.

The tracked files under `data/` are never modified by normal runs. A reviewer
can inspect each layer independently or call `workflow.run_date_range()` for
the complete flow.
