import pandas as pd

from vanke_dtd_pipeline.daily_dtd_calculator import _next_hk_open, load_hk_calendar
from vanke_dtd_pipeline.project_data_paths import repository_data


def test_first_eligible_hong_kong_day_after_confirmed_history_is_20251215():
    calendar = load_hk_calendar(repository_data().trading_calendar)
    next_open = _next_hk_open(calendar, pd.Timestamp("2025-12-12"))
    assert next_open == pd.Timestamp("2025-12-15")
