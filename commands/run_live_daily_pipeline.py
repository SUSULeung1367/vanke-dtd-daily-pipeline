"""Run the standard daily pipeline for one date using live market data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vanke_dtd_pipeline.pipeline_config import DEFAULT_COMPANY
from vanke_dtd_pipeline.daily_pipeline_runner import run_date_range


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="YYYYMMDD")
    parser.add_argument("--company", type=int, default=DEFAULT_COMPANY)
    parser.add_argument("--workspace", type=Path, default=ROOT / "runtime" / "live_daily_workspace")
    parser.add_argument("--keep", action="store_true", help="Reuse an existing workspace")
    args = parser.parse_args()
    result = run_date_range(
        args.date, args.date, project_dir=ROOT, workspace_dir=args.workspace,
        mode="LIVE", reset=not args.keep, company=args.company,
    )
    print(f"Workspace: {result.workspace}")
    print(result.daily_results.to_string(index=False))


if __name__ == "__main__":
    main()
