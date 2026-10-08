# Daily review guide — Checker and Marker

## Checker: normal daily approval

A Checker reviews a normal daily result after automated QC and a provisional
DTD are available. The Checker can approve or reject it, but cannot directly
edit released history.

## Marker: warnings and exceptions

A Marker handles data warnings, exceptions and manual changes. These cases are
not normal daily approvals; they need documented review and an audit record.

## Record protection

Confirmed history is append-only. The implementation must never provide a
routine code path that overwrites or deletes an already released confirmed
date. For the detailed workflow, see
`docs/reference/production_workflow_and_control_specification.md`.
