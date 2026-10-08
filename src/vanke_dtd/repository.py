"""Repository data layout and isolated runtime workspace setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepositoryData:
    """Locations of tracked, non-generated repository inputs."""

    root: Path

    @property
    def baseline_vanke(self) -> Path:
        return self.root / "data" / "baseline" / "vanke.xlsx"

    @property
    def historical_market_reference(self) -> Path:
        return self.root / "data" / "baseline" / "Daily_Calendar.xlsx"

    @property
    def trading_calendar(self) -> Path:
        return self.root / "data" / "controlled" / "China_HK_Trading_Calendar.xlsx"

    @property
    def issued_capital_datalog(self) -> Path:
        return self.root / "data" / "controlled" / "Vanke Issued Capital DataLog.xlsx"

    @property
    def risk_free_cache(self) -> Path:
        return self.root / "data" / "controlled" / "HKMA_Risk_Free_Daily.xlsx"

    @property
    def replay_datalog(self) -> Path:
        return self.root / "data" / "replay" / "Vanke_Daily_Datalog.xlsx"


def repository_root() -> Path:
    """Return the repository root when installed from this source tree."""
    return Path(__file__).resolve().parents[2]


def repository_data(root: str | Path | None = None) -> RepositoryData:
    return RepositoryData(Path(root or repository_root()).resolve())


def validate_repository_data(data: RepositoryData) -> None:
    """Fail early with a clear message when tracked source data are absent."""
    required = [
        data.baseline_vanke,
        data.trading_calendar,
        data.issued_capital_datalog,
        data.risk_free_cache,
        data.replay_datalog,
    ]
    missing = [str(path.relative_to(data.root)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing tracked source data: " + ", ".join(missing))
