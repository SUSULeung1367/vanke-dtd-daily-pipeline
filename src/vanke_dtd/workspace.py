"""Paths for one generated, isolated pipeline run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yfinance as yf


@dataclass(frozen=True)
class WorkspacePaths:
    root: Path

    @property
    def confirmed_vanke(self) -> Path:
        return self.root / "vanke.xlsx"

    @property
    def calendar(self) -> Path:
        return self.root / "China_HK_Trading_Calendar.xlsx"

    @property
    def issued_capital(self) -> Path:
        return self.root / "Vanke Issued Capital DataLog.xlsx"

    @property
    def risk_free_cache(self) -> Path:
        return self.root / "HKMA_Risk_Free_Daily.xlsx"

    @property
    def daily_datalog(self) -> Path:
        return self.root / "Vanke_Daily_Datalog.xlsx"

    @property
    def temporary_input(self) -> Path:
        return self.root / "vanke_dtd_temporary_data.xlsx"

    @property
    def temporary_output(self) -> Path:
        return self.root / "temporary_output.xlsx"

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
            "No runtime workspace is configured. Use workflow.prepare_demo_workspace() "
            "or workspace.configure_workspace() first."
        )
    return _current
