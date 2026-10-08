"""Paths for the tracked standard inputs and fixed basic-test fixture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepositoryData:
    """Locations of tracked, non-generated repository inputs."""

    root: Path

    @property
    def confirmed_history(self) -> Path:
        return (
            self.root / "data" / "standard_inputs" / "confirmed_history"
            / "vanke_confirmed_history.xlsx"
        )

    @property
    def historical_market_reference(self) -> Path:
        return (
            self.root / "data" / "standard_inputs" / "confirmed_history"
            / "vanke_historical_market_cap_reference.xlsx"
        )

    @property
    def trading_calendar(self) -> Path:
        return (
            self.root / "data" / "standard_inputs" / "controlled_reference_data"
            / "china_hk_trading_calendar.xlsx"
        )

    @property
    def company_data(self) -> Path:
        return (
            self.root / "data" / "standard_inputs" / "controlled_reference_data"
            / "vanke_effective_dated_company_data.xlsx"
        )

    @property
    def risk_free_rate_cache(self) -> Path:
        return (
            self.root / "data" / "standard_inputs" / "controlled_reference_data"
            / "hkma_364_day_bill_yield_cache.xlsx"
        )

    @property
    def basic_test_market_data(self) -> Path:
        return (
            self.root / "data" / "basic_test_fixture"
            / "vanke_market_data_20251213_to_20251219.xlsx"
        )


def repository_root() -> Path:
    """Return the repository root when installed from this source tree."""
    return Path(__file__).resolve().parents[2]


def repository_data(root: str | Path | None = None) -> RepositoryData:
    return RepositoryData(Path(root or repository_root()).resolve())


def validate_repository_data(data: RepositoryData) -> None:
    """Fail early with a clear message when tracked source data are absent."""
    required = [
        data.confirmed_history,
        data.trading_calendar,
        data.company_data,
        data.risk_free_rate_cache,
        data.basic_test_market_data,
    ]
    missing = [str(path.relative_to(data.root)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing tracked source data: " + ", ".join(missing))
