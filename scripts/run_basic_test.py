"""Run the deterministic five-day Vanke basic local test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vanke_dtd.demo_settings import DEFAULT_COMPANY, DEFAULT_END_DATE, DEFAULT_START_DATE
from vanke_dtd.workflow import run_date_range


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START_DATE, help="YYYYMMDD inclusive")
    parser.add_argument("--end", default=DEFAULT_END_DATE, help="YYYYMMDD inclusive")
    parser.add_argument("--company", type=int, default=DEFAULT_COMPANY)
    parser.add_argument("--workspace", type=Path, default=ROOT / "runtime" / "demo_workspace")
    parser.add_argument("--keep", action="store_true", help="Reuse the workspace instead of resetting it")
    args = parser.parse_args()
    result = run_date_range(
        args.start, args.end, project_dir=ROOT, workspace_dir=args.workspace,
        mode="REPLAY", reset=not args.keep, company=args.company,
    )
    print(f"Workspace: {result.workspace}")
    print("\nDaily results")
    print(result.daily_results.to_string(index=False))
    print("\nTemporary DTD")
    print(result.temporary_dtd.to_string(index=False))


if __name__ == "__main__":
    main()
