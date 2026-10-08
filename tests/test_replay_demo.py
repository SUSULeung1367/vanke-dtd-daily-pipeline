import pandas as pd

from vanke_dtd.workflow import run_date_range


def test_default_replay_produces_the_five_expected_trading_day_outputs(tmp_path):
    result = run_date_range(
        "20251213",
        "20251219",
        workspace_dir=tmp_path / "replay",
        mode="REPLAY",
        reset=True,
    )
    statuses = result.daily_results.set_index("Date")["DTD_Status"].to_dict()
    assert statuses["2025-12-13"] == "SKIPPED_HK_CLOSED"
    assert statuses["2025-12-14"] == "SKIPPED_HK_CLOSED"
    assert [int(value) for value in result.temporary_dtd["Date"]] == [
        20251215,
        20251216,
        20251217,
        20251218,
        20251219,
    ]
    baseline = pd.read_excel("data/baseline/vanke.xlsx", sheet_name="Input")
    assert len(baseline) == 493
