"""Display or record a Checker decision for one daily runtime workspace."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vanke_dtd_pipeline.checker_daily_result_reviewer import build_checker_table, confirm_dates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT / "runtime" / "basic_test_workspace")
    parser.add_argument("--decision", choices=["PENDING", "APPROVE", "REJECT"], default="PENDING")
    parser.add_argument("--checker", help="Required for APPROVE or REJECT")
    parser.add_argument("--dates", nargs="+", help="YYYYMMDD dates for APPROVE or REJECT")
    args = parser.parse_args()
    if args.decision == "PENDING":
        print(build_checker_table(args.workspace).to_string(index=False))
        return
    if not args.checker or not args.dates:
        parser.error("--checker and --dates are required for APPROVE or REJECT")
    print(confirm_dates(args.workspace, args.dates, args.checker, args.decision).to_string(index=False))


if __name__ == "__main__":
    main()
