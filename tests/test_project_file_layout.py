from vanke_dtd_pipeline.project_data_paths import repository_data, validate_repository_data


def test_tracked_data_layout_is_complete():
    data = repository_data()
    validate_repository_data(data)
    assert data.confirmed_history.parent.name == "confirmed_history"
    assert data.trading_calendar.parent.name == "controlled_reference_data"
    assert data.basic_test_market_data.parent.name == "basic_test_fixture"


def test_runtime_is_not_a_tracked_data_location():
    data = repository_data()
    assert "runtime" not in data.confirmed_history.parts
    assert "runtime" not in data.basic_test_market_data.parts
