# Data guide — inputs only, never generated results

This directory contains tracked inputs. It is not a runtime-output directory.

- `standard_inputs/` contains confirmed history, the trading calendar, company
  data and the risk-free-rate cache used by the standard daily pipeline.
- `basic_test_fixture/` contains the fixed saved market data used only by the
  basic local test.

Read [`../docs/data_guide.md`](../docs/data_guide.md) before editing any file
here. Commands copy what they need into `runtime/`; normal runs must not modify
this directory.
