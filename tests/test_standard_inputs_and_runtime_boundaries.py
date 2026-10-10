from vanke_dtd_pipeline.project_data_paths import repository_data, validate_repository_data


def test_required_standard_inputs_and_basic_test_fixture_are_available():
    data = repository_data()
    validate_repository_data(data)
    assert data.confirmed_history.parent.name == "confirmed_history"
    assert data.trading_calendar.parent.name == "controlled_reference_data"
    assert data.basic_test_market_data.parent.name == "basic_test_fixture"


def test_generated_runtime_results_are_not_tracked_input_data():
    data = repository_data()
    assert "runtime" not in data.confirmed_history.parts
    assert "runtime" not in data.basic_test_market_data.parts
