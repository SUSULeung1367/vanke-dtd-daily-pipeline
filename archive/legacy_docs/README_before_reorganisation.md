# Vanke Daily DTD Pipeline

This repository contains an offline-replayable demonstration of the Vanke daily data-to-DTD workflow. It separates daily input/QC, calendar-controlled DTD calculation, and Checker-controlled append-only release.

The controlled Excel inputs and the saved daily observation log are tracked because they are required for deterministic `REPLAY` mode. Generated workspaces, Temporary Input/Output files, and local caches are deliberately excluded from Git.

## Setup

Open a terminal in this folder and run:

```bash
conda create -n vanke-dtd python=3.13 -y
conda activate vanke-dtd
python -m pip install -r requirements.txt
jupyter notebook
```

Keep all supplied Python, notebook and Excel files in the same project folder. `REPLAY` is deterministic and offline; `LIVE` calls Yahoo Finance and HKMA and should be used only when live retrieval is intended.

## Script entry points

- `vanke_dtd_pipeline.py` coordinates a range run in an isolated workspace.
- `daily_data_pipeline.py` handles retrieval/replay, QC, and Temporary Input preparation.
- `dtd_calendar_test_module.py` applies calendar controls and calculates DTD.
- `vanke_data_confirm_checker.py` builds the Checker review table and performs atomic, append-only approval or rejection.

`Vanke_Daily_Datalog.xlsx` is the controlled source of saved observations for `REPLAY`; do not remove it from the project.

## Step 1 Run the date-range demo

Open `vanke_pipeline_demo.ipynb`.

Change only:

```python
START_DATE = "20251213"
END_DATE = "20251219"
```

Then use **Restart Kernel and Run All Cells**.

- The range is inclusive.
- One selected calendar day produces one Daily Result row.
- Three selected calendar days produce three Daily Result rows.
- Weekends and HK holidays are shown as skipped and do not produce DTD.
- The notebook prints Daily QC, Vanke Temporary Input, Temporary DTD and the updated clean DTD Input table.
- The default `MODE = "REPLAY"` is deterministic and does not call an API.
- Set `MODE = "LIVE"` only when live Yahoo Finance and HKMA retrieval is required.

All notebook demo writes go to `demo_workspace`. The original `vanke.xlsx` is not changed. `demo_workspace` and all generated Temporary artifacts are ignored by Git.

## Data sources

- Yahoo Finance through `yfinance`: Vanke A-share close (`000002.SZ`), Vanke H-share close (`2202.HK`) and CNY/HKD FX (`CNYHKD=X`).
- Hong Kong Monetary Authority API: 364-day Exchange Fund Bill yield used as the 12-month risk-free proxy.
- Supplied controlled files: trading calendar, issued capital, balance-sheet inputs and confirmed history.

The A-share market value is converted from CNY to HKD with the daily CNY/HKD rate. The H-share market value is already in HKD. Both are divided by 1,000,000 so market capitalization and balance-sheet fields use HKD millions. Full URLs, transformations and limitations are in the technical specification.

## Step 2 Review and confirm

Open `vanke_data_confirm_cheker.ipynb` after Step 1.

1. Run the setup and review cells.
2. Read the combined table containing Temporary Input, DTD and QC.
3. Enter the Checker name and dates.
4. Change `CHECKER_DECISION` from `"PENDING"` to `"APPROVE"` or `"REJECT"`.
5. Run the confirmation cell.

Only rows with passing automated QC, a calculated DTD and no Marker requirement can be released by the normal Checker path. Approval appends Input and Output rows to the workspace's `vanke.xlsx` and records a confirmation-log entry; historical rows are never overwritten. A rejection is recorded without releasing the data.

## Reproducible verification

Run REPLAY in a new temporary workspace rather than the repository root:

```powershell
@'
from pathlib import Path
import tempfile
from vanke_dtd_pipeline import run_date_range

workspace = Path(tempfile.mkdtemp(prefix="vanke-dtd-replay-"))
result = run_date_range(
    "20251213", "20251219",
    project_dir=Path.cwd(),
    workspace_dir=workspace,
    mode="REPLAY",
    reset=True,
)
print(result.workspace)
print(result.daily_results.to_string(index=False))
'@ | python
```

Then use `vanke_data_confirm_cheker.ipynb`, or `build_checker_table()` and `confirm_dates()` from `vanke_data_confirm_checker.py`, to review and approve only the passing, pending rows. A clean verification on 2026-10-02 confirmed that 2025-12-13 and 2025-12-14 were skipped as HK-closed dates, while 2025-12-15 through 2025-12-19 passed QC, produced DTD outputs, and changed from `PENDING_CHECKER` to `RELEASED` after approval.

## Repository hygiene

Source code, notebooks, specifications, controlled inputs, and the replay data log are tracked. `.gitignore` excludes caches, `demo_workspace`, Jupyter/editor by-products, `temporary_output.xlsx`, `vanke_dtd_temporary_data.xlsx`, and the Checker's atomic intermediate files. Create a fresh isolated workspace for every demo or validation run.

Detailed design is in `VANKE_DTD_PRODUCTION_WORKFLOW_AND_CONTROL_SPECIFICATION.md`. Section 2 gives the full production process and Checker/Marker responsibilities. Section 12 gives the DTD assumptions, equations and limitations.
