"""Clear file paths for one generated, isolated pipeline run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yfinance as yf


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path

    @property
    def confirmed_history(self) -> Path:
        return self.root / "vanke_confirmed_history.xlsx"

    @property
    def calendar(self) -> Path:
        return self.root / "china_hk_trading_calendar.xlsx"

    @property
    def company_data(self) -> Path:
        return self.root / "vanke_effective_dated_company_data.xlsx"

    @property
    def risk_free_rate_cache(self) -> Path:
        return self.root / "hkma_364_day_bill_yield_cache.xlsx"

    @property
    def market_data_audit(self) -> Path:
        return self.root / "daily_market_data_audit.xlsx"

    @property
    def pending_review_input(self) -> Path:
        return self.root / "daily_dtd_input_pending_review.xlsx"

    @property
    def pending_review_output(self) -> Path:
        return self.root / "daily_dtd_output_pending_review.xlsx"

    @property
    def yfinance_cache(self) -> Path:
        return self.root / ".yfinance_cache"


_current: Optional[WorkspacePaths] = None


def configure_workspace(root: str | Path) -> WorkspacePaths:
    """Configure file-backed stages to use one generated workspace only."""
    global _current
    paths = WorkspacePaths(Path(root).resolve())
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.yfinance_cache.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(paths.yfinance_cache))
    _current = paths
    return paths


def current_workspace() -> WorkspacePaths:
    if _current is None:
        raise RuntimeError(
            "No runtime workspace is configured. Use "
            "daily_pipeline_runner.prepare_runtime_workspace() or "
            "runtime_workspace.configure_workspace() first."
        )
    return _current
