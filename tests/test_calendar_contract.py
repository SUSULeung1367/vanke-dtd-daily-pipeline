import pandas as pd

from vanke_dtd.dtd import _next_hk_open, load_hk_calendar
from vanke_dtd.repository import repository_data


def test_first_hk_open_day_after_the_confirmed_baseline_is_20251215():
    calendar = load_hk_calendar(repository_data().trading_calendar)
    next_open = _next_hk_open(calendar, pd.Timestamp("2025-12-12"))
    assert next_open == pd.Timestamp("2025-12-15")
