"""Verify the standard pipeline locally with the fixed five-day basic test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vanke_dtd_pipeline.pipeline_config import DEFAULT_COMPANY
from vanke_dtd_pipeline.daily_pipeline_runner import run_date_range


BASIC_TEST_START_DATE = "20251213"
BASIC_TEST_END_DATE = "20251219"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=BASIC_TEST_START_DATE, help="YYYYMMDD inclusive")
    parser.add_argument("--end", default=BASIC_TEST_END_DATE, help="YYYYMMDD inclusive")
    parser.add_argument("--company", type=int, default=DEFAULT_COMPANY)
    parser.add_argument("--workspace", type=Path, default=ROOT / "runtime" / "basic_test_workspace")
    parser.add_argument("--keep", action="store_true", help="Reuse the workspace instead of resetting it")
    args = parser.parse_args()
    result = run_date_range(
        args.start, args.end, project_dir=ROOT, workspace_dir=args.workspace,
        mode="BASIC_TEST", reset=not args.keep, company=args.company,
    )
    print(f"Workspace: {result.workspace}")
    print("\nBasic-test daily results")
    print(result.daily_results.to_string(index=False))
    print("\nPending-review DTD output")
    print(result.pending_review_dtd_output.to_string(index=False))


if __name__ == "__main__":
    main()
