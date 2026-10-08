# Data guide — tracked source files

This directory contains the tracked inputs needed to understand or reproduce
the Vanke demonstration. It is not a runtime output directory.

- `baseline/` contains the supplied confirmed Vanke history and its historical
  market-cap reference.
- `controlled/` contains the calendar and effective-dated source inputs used
  by a run.
- `replay/` contains saved daily observations used by the deterministic demo.

Read [`../docs/data_dictionary.md`](../docs/data_dictionary.md) before editing
any file here. Normal scripts copy the necessary inputs into `runtime/`; they
must not modify this directory.
