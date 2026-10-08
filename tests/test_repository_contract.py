from vanke_dtd.repository import repository_data, validate_repository_data


def test_tracked_data_layout_is_complete():
    data = repository_data()
    validate_repository_data(data)
    assert data.baseline_vanke.parent.name == "baseline"
    assert data.trading_calendar.parent.name == "controlled"
    assert data.replay_datalog.parent.name == "replay"


def test_runtime_is_not_a_tracked_data_location():
    data = repository_data()
    assert "runtime" not in data.baseline_vanke.parts
    assert "runtime" not in data.replay_datalog.parts
