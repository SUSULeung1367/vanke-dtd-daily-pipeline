# Pytest suite — business rule checks

`test_` is required by pytest so it can discover the files. The rest of each
filename states the rule being checked.

| Pytest file | Rule it verifies |
|---|---|
| `test_basic_pipeline_end_to_end.py` | The fixed five-day basic test creates sequential pending-review DTD outputs. |
| `test_hong_kong_trading_day_sequence.py` | The first eligible Hong Kong date follows the confirmed-history anchor. |
| `test_standard_inputs_and_runtime_boundaries.py` | Required standard inputs exist and generated runtime results are not tracked inputs. |
| `conftest.py` | Pytest setup: makes the `src/` package importable. This filename is required by pytest. |

Run every automated check with:

```powershell
pytest
```
