# Vanke DTD Production Workflow and Control Specification

## 1 Purpose and core rule

This document explains how the demonstration implements a repeatable daily Distance-to-Default pipeline. It covers the data contract, date-range processing, input quality control, DTD calculation boundary, Temporary-to-Production approval and Checker/Marker responsibilities.

The design separates automated preparation from human release. A daily run may prepare new observations even when no reviewer is available. Prepared observations remain in Temporary until the required approval is complete. Confirmed history is append-only.

The governing rule is: Temporary data may be changed through a controlled workflow, while released Production data are immutable. A correction to Production must create a new controlled version; it must never overwrite or delete the historical record.

## 2 Production process and control ownership

### 2.1 End-to-end production process

The intended scheduled run is 7:00 PM each calendar day. The notebook simulates the same process for an inclusive date range. Each date is processed separately and in order.

1. Read the controlled China/Hong Kong trading calendar.
2. Read the latest Vanke Company DataLog record effective on or before the processing date.
3. Retrieve or replay the required market prices, CNY/HKD rate and HKMA risk-free rate.
4. Apply the appropriate open/closed market rule.
5. Build one daily Temporary DTD Input row when the date is eligible.
6. Run Input QC.
7. Calculate provisional DTD for an eligible HK trading date.
8. Run calculation and output checks.
9. Keep the record in `PENDING` state until human review.
10. Present Temporary Input, provisional DTD and QC in the Checker notebook.
11. Release a normal row after Checker approval, or route an exception/change to Marker review.
12. Append approved Input and DTD to Production and write the approval audit record.

Daily preparation does not wait for the Checker. Several Temporary dates may accumulate while Production remains unchanged. Human approval is a release control, not a prerequisite for collecting and calculating new daily observations.

### 2.2 Roles and permissions

| Activity | Automated pipeline | Checker | Marker |
|---|---|---|---|
| Retrieve daily data and build Temporary record | Yes | Review | Review exceptions |
| Run Input QC and provisional DTD | Yes | Review results | Review exception reruns |
| Approve a normal unchanged record | No | Yes | Not required |
| Correct one Temporary date through controlled code | No | Yes | May correct during exception review |
| Directly edit an Excel Temporary cell | No | No | No |
| Approve a manual change or QC exception | No | Required | Required |
| Directly update or delete released Production | No | No | No |
| Request a correction to released Production | No | Yes | Review required |
| Approve a corrected Production version | No | Required | Required |

### 2.3 Checker responsibility

The Checker performs the daily first-level review. The Checker checks the Temporary DTD Input, source dates, market-calendar treatment, Input QC, provisional DTD, DTD QC, warnings and continuity with the previous completed HK trading date. A normal unchanged row may be approved by the Checker alone.

The Checker may correct a date-specific problem only through the controlled Python workflow and only one `Data_Date` per correction request. The original value, new value, reason and Checker identity must be recorded. A Checker change automatically changes the record to `MANUAL_EXCEPTION`, invalidates the earlier QC and provisional DTD, triggers recalculation, and requires Marker approval. The Checker cannot update, overwrite or delete a released Production row.

### 2.4 Marker responsibility

The Marker is the second-level reviewer for QC exceptions, manual changes and corrections to previously released data. The Marker is not required for routine rows that pass QC and have not been changed.

The Marker reviews the investigation evidence, old and new values, reason, rerun QC, recalculated DTD and DTD QC. During exception review, the Marker may enter or request a further controlled change to the Temporary record or correction copy; the Marker must never edit Production directly. A Marker-originated change creates a new change-log entry, invalidates the previous calculation again, and requires the Checker to re-review the recalculated record. Both roles must approve the final exception version. A person who changes a value cannot release that changed value without the other role's approval.

### 2.5 Normal release, exception release and Production correction

For a normal record, the Checker approves after QC passes and the Input/DTD pair is appended to Production. Marker approval is not required.

For a QC exception or manual change, the record remains outside Production. The controlled correction is applied in Temporary, earlier QC and DTD are invalidated, all checks are rerun, and the record enters `MARKER_PENDING`. Release is allowed only after Checker and Marker approval.

If a problem is found after release, the system creates a correction copy in Temporary. The original Production version remains available. After correction, rerun and dual approval, the new version becomes `CURRENT` and the older version becomes `SUPERSEDED`. Neither role has a code path that overwrites historical Production.

## 3 Implementation boundary

The implementation has four technical stages:

1. Read the controlled trading calendar and daily source observations.
2. Build and validate one clean DTD Input row for each selected calendar date.
3. Calculate DTD only for eligible Hong Kong trading dates in continuous order.
4. Present Temporary Input, Temporary DTD and QC to the Checker before release.

`daily_input_builder.py` prepares and checks daily Input. `daily_dtd_calculator.py`
enforces calendar continuity and calculates DTD. `daily_pipeline_runner.py`
coordinates the standard pipeline and exposes the date-range interface.

The submitted Checker notebook implements the normal unchanged-record approval path and blocks any row requiring Marker review. The controlled manual-correction and versioned Production-correction rules above define the required production control. They are deliberately not represented as direct spreadsheet editing.

## 4 File contract

| File | Purpose | Write rule |
|---|---|---|
| `vanke_confirmed_history.xlsx` | Confirmed Input and DTD Output history | Append approved new dates only |
| `china_hk_trading_calendar.xlsx` | Controlled China and Hong Kong open/closed status | Read-only during a run |
| `vanke_effective_dated_company_data.xlsx` | Effective-dated shares and financial data | Read the latest record effective on or before the processing date |
| `hkma_364_day_bill_yield_cache.xlsx` | Local HKMA 12-month yield cache | Add an exact-date observation in LIVE mode |
| `daily_market_data_audit.xlsx` | Daily result and API-attempt audit | Add or update the daily run record |
| `daily_dtd_input_pending_review.xlsx` | QC-approved incremental DTD Input | Append eligible new dates; no confirmed history |
| `daily_dtd_output_pending_review.xlsx` | Provisional incremental DTD | Append continuous HK trading dates only |
| `Confirmation_Log` sheet | Checker decision and release audit | Append one decision record |

The basic test and demos use `basic_test_workspace` so reviewers can test
releases without changing the supplied confirmed-history baseline.

## 5 Date-range behavior

`START_DATE` and `END_DATE` are inclusive calendar dates in `YYYYMMDD` format. The orchestrator loops through every calendar date in order. This makes a multi-day demonstration behave as repeated daily runs, not as one bulk replacement.

- If start and end are the same, one Daily Result row is returned.
- If the range contains three calendar dates, three Daily Result rows are returned.
- A weekend or HK holiday remains visible in the Daily Result but does not enter Temporary Input or Temporary DTD.
- An HK-open date must be the next HK trading date after the latest completed confirmed or temporary DTD date.
- A request that jumps over an unprocessed HK trading date is blocked.
- A date outside controlled calendar coverage is blocked.

This ordering prevents future information from entering an earlier calculation and makes each daily decision auditable.

## 6 Demonstration modes

### 6.1 BASIC_TEST profile

`BASIC_TEST` is the fixed local test profile. It reads saved daily source and QC
observations from `data/basic_test_fixture/` and does not call an external API.
This makes the test deterministic and isolates reviewers from network
availability, vendor changes and historical API revisions.

`BASIC_TEST` still applies the same calendar gate, pending-review Input schema,
DTD calculation, trading-day continuity and approval controls. An HK-open date
without a saved basic-test observation is blocked with a clear message.

### 6.2 LIVE mode

LIVE calls Yahoo Finance for China Vanke A-share close, Hong Kong Vanke close and CNY/HKD FX, and calls the HKMA endpoint for the 364-day Exchange Fund Bill yield. Each request uses bounded retries and records each attempt. A source failure or exact-date mismatch cannot enter Temporary Input.

LIVE mode is the standard daily retrieval path. `BASIC_TEST` is appropriate for
local verification because its result does not depend on network state.

## 7 Data sources and automated access

| Input | Programmatic source | Access used | Limitation |
|---|---|---|---|
| China Vanke A-share close | Yahoo Finance historical data for `000002.SZ` | `https://finance.yahoo.com/quote/000002.SZ/history/` through `yfinance` | Reputable public aggregator, not the exchange's contractual market-data feed |
| China Vanke H-share close | Yahoo Finance historical data for `2202.HK` | `https://finance.yahoo.com/quote/2202.HK/history/` through `yfinance` | May be revised or temporarily unavailable |
| CNY/HKD exchange rate | Yahoo Finance historical data for `CNYHKD=X` | `https://finance.yahoo.com/quote/CNYHKD=X/history/` through `yfinance` | Daily timestamp and vendor convention must be checked |
| 12-month risk-free proxy | Hong Kong Monetary Authority | `https://api.hkma.gov.hk/public/market-data-and-statistics/monthly-statistical-bulletin/efbn/efbn-yield-daily` field `efb_364d` | Publication may be delayed; an exact HK-open-date value is required |
| Trading-day status | Supplied controlled calendar | Local `Daily Calendar` sheet | Coverage must be maintained and independently reviewed |
| Issued capital and financial inputs | Supplied Vanke DataLog and confirmed history | Effective-dated local records | New disclosures require a new reviewed DataLog record |

The online calls are parameterized by data date, use bounded retries and store
attempt-level evidence. A successful response is not enough by itself: the
returned source date and numeric value must also pass QC. `BASIC_TEST` uses
previously saved daily observations so local verification remains repeatable
when external services are unavailable.

## 8 Market-day rules

| China market | Hong Kong market | Daily treatment | DTD treatment |
|---|---|---|---|
| Open | Open | Require exact-date China close, HK close, FX and risk-free rate | Calculate if QC passes |
| Closed | Open | Carry the most recent China close; require exact-date HK data | Calculate if QC passes |
| Open | Closed | Record the day and carry prior HK data where needed for audit | Do not calculate DTD |
| Closed | Closed | Record expected closure | Do not calculate DTD |

`HK_Open` is the authoritative DTD eligibility flag. `China_Open` affects how the China price component is sourced but does not independently decide whether DTD is produced.

## 9 Incremental Input construction

Daily market capitalization is expressed in HKD millions:

`China market cap = China close x China shares x CNY/HKD / 1,000,000`

`Hong Kong market cap = HK close x Hong Kong shares / 1,000,000`

`Total market cap = China market cap + Hong Kong market cap`

The risk-free input is the HKMA 12-month proxy. A stored value such as `2.45` means 2.45 percent; the DTD calculation converts it to `0.0245`.

The assignment period assumes no new financial statement after 12 December 2025. Current liabilities, long-term borrowings, total liabilities and total assets are therefore carried forward. In a continuing production system, the latest DataLog record with effective date less than or equal to the processing date must be used. A new disclosure creates a new effective-dated record; it does not overwrite the previous regime.

## 10 Input quality control

An Input row is blocked when any required source is unavailable for a date on which it must be exact, a source date is inconsistent with the controlled calendar, a required numeric field is missing or non-positive, FX is outside 0.50 to 2.00, or the risk-free rate is outside -5 to 20 percent.

The following changes require investigation rather than silent acceptance:

- China or Hong Kong close changes by more than 30 percent;
- FX changes by more than 5 percent;
- risk-free rate changes by more than 1 percentage point;
- total market capitalization changes by more than 30 percent.

Day-on-day market-cap QC compares the new observation with the latest available validated observation, including a prior Temporary row. It does not repeatedly compare every new date with the final confirmed date.

`PASS` and `PASS_WITH_WARNING` may proceed when no manual-review flag exists. `REVIEW_REQUIRED` and `FAIL` are blocked from normal release.

## 11 Updated clean Input and schema consistency

The final clean Input is produced by combining confirmed history with QC-approved Temporary Input. The output preserves the original eight columns and their meanings:

`Comp_no`, `Date`, `CUR_MKT_CAP(HKD)`, `BS_CUR_LIAB(HKD)`, `BS_LT_BORROW(HKD)`, `BS_TOT_LIAB2(HKD)`, `BS_TOT_ASSET(HKD)` and `Risk_Free_Rate`.

Dates are normalized before comparison. Numeric columns are converted explicitly. Financial fields are carried forward only when an applicable earlier value exists. A company/date duplicate is resolved in favor of confirmed history. Historical rows are not rewritten. The demo notebook prints both the incremental Temporary Input and the combined updated clean Input so the schema and appended dates can be inspected directly.

## 12 DTD calculation assumptions and limitations

The calculation is a NUS-CRI-methodology-consistent reconstruction. It does not claim to reproduce the proprietary production engine or proprietary calibrated parameters.

### 12.1 Input and frequency assumptions

| Assumption | Implementation |
|---|---|
| Daily incremental variables | `CUR_MKT_CAP(HKD)` and `Risk_Free_Rate` are updated for each eligible HK trading date |
| Financial-statement variables | Current liabilities, long-term borrowings, total liabilities and book total assets are carried forward until a new effective-dated financial record exists |
| Currency | Market capitalization and balance-sheet variables are HKD millions |
| Risk-free convention | A value such as `2.46` means 2.46 percent and is converted to `0.0246` for valuation |
| Information cutoff | A target-date calculation uses only observations dated on or before that target date |
| Duplicate company/date | Confirmed history has priority over Temporary data |

`BS_TOT_ASSET(HKD)` is book total assets. It is not the unobserved Merton market value of assets `V`. Book assets may stay unchanged while `V` changes every trading day.

### 12.2 Default-point assumption

Other liabilities are defined as:

`OL = Total Liabilities - Current Liabilities - Long-term Borrowings`

The default point is:

`L = Current Liabilities + 0.5 x Long-term Borrowings + delta x OL`

This implementation uses `delta = 0.50`. This is an explicit modelling assumption for the packaged Vanke reconstruction. NUS-CRI production uses sector/economy calibration and smoothing; the supplied workbook does not contain the cross-sectional information needed to reproduce that proprietary calibration exactly.

### 12.3 Estimation-window assumptions

- The rolling estimation window is the latest one-year period ending on the target date.
- At least 50 valid observations are required.
- The implementation uses 250 trading days per year, so the interval is represented as `1/250`.
- Consecutive retained Input rows are assumed to be valid trading observations.
- Maturity in the equity-option inversion is one year.
- Candidate asset volatility is constrained to the numerical search range `0.005` to `1.50`.

If a source later supplies an explicit valid-trading-day gap or volume flag, the fixed `1/250` interval should be replaced with the observed interval series for closer production fidelity.

### 12.4 Asset-volatility and asset-value assumptions

For each candidate asset volatility `sigma`, the module solves the Merton/Black-Scholes equity equation for market asset value `V` on each observation in the rolling window:

`E = V x N(d1) - exp(-rT) x L x N(d2)`

Book total assets are used to standardize the `V/A` transformed series in the likelihood. Asset volatility is estimated by maximizing the one-year transformed-data likelihood. After estimating `sigma`, the same equity equation is solved again for the target-date `V` using target-date equity market capitalization, default point and risk-free rate.

### 12.5 DTD assumption

Under the supplied CRI drift treatment, the drift contribution used in the final distance measure cancels. The implemented target-date measure is:

`DTD = ln(V / L) / sigma`

The output is a model signal, not a direct statement that default will or will not occur. The calculation must be described as a reconstruction consistent with the published structure, not as an exact CRI production number.

### 12.6 Calculation controls and limitations

The calculation is blocked when the target date is absent, fewer than 50 valid observations exist, market capitalization or default point is non-positive, the risk-free convention is invalid, the market-asset root cannot be bracketed, or sigma optimization does not converge.

Before release, unusually large changes in DTD or sigma should be compared with market-cap changes, risk-free movements, source-date changes and any Company DataLog update. The demo validates calculation availability and sequence but does not claim to reproduce every proprietary CRI smoothing or calibration step.

Methodology references:

- NUS Credit Research Initiative Technical Report Version 2023 Update 1: `https://d.nuscri.org/static/pdf/Technicalreport_2023.pdf`
- NUS-CRI technical documents: `https://nuscri.org/en/technical_document/`

## 13 Detailed Checker review and normal release

The Checker notebook combines Temporary Input, provisional DTD and daily QC into one table. The normal Checker may approve only when:

- Automated QC is `PASS`;
- the provisional DTD exists;
- no manual-review or exception flag exists;
- the date is not already released.

The Checker enters a name, selects dates and explicitly changes the decision from `PENDING` to `APPROVE` or `REJECT`. `PENDING` never writes a file.

An approval appends both the Input row and DTD row to the demo confirmed workbook in one atomic workbook replacement. Existing confirmed dates are never updated or deleted. The same workbook receives a Confirmation Log row containing the decision time, data date, Checker, QC state, Marker requirement and release status.

## 14 Detailed Marker and exception control

Routine data that pass QC and have not been manually changed require Checker approval only. Marker approval is not forced for every normal day.

A Marker is required when automated QC identifies an exception or the Checker changes Temporary data. A manual change must preserve the old value, new value, reason and Checker identity; invalidate earlier QC and provisional DTD; rerun Input QC and DTD QC; and remain unreleased until Marker approval.

The normal Checker notebook refuses to release a row with `Marker_Required = True`. This prevents a user from bypassing the exception workflow by changing a configuration value.

If an error is found after release, the confirmed row must not be edited in place. A corrected copy is prepared in Temporary, revalidated, approved by Checker and Marker, and released as a new version. The older production version remains available and is marked superseded in a full production implementation.

## 15 Status model and audit evidence

| Status | Meaning | Production eligible? |
|---|---|---|
| `PENDING` | Automatically prepared and waiting for Checker review | No |
| `QC_EXCEPTION` | Automated QC or expected/observed market mismatch | No |
| `MANUAL_EXCEPTION` | Checker or Marker changed Temporary data | No |
| `CHECKER_APPROVED` | Normal unchanged row approved by Checker | Yes |
| `MARKER_PENDING` | Exception or change waiting for second-level review | No |
| `APPROVED_EXCEPTION` | Final exception version approved by Checker and Marker | Yes |
| `RELEASED` | Published Production version | Already released |
| `SUPERSEDED` | Older released version retained after correction | Historical only |
| `REJECTED` | Human reviewer rejected the proposed record | No |

The Checker table label `PENDING_CHECKER` is the demonstration display of the governance state `PENDING`.

The Daily Update Log should retain a unique log ID, update time, data date, affected table, action and system/user identity. A manual-change or correction log must additionally retain change ID, table and field, old value, new value, reason, Checker, Marker status, approval time and the link between old and new Production versions.

## 16 Failure and recovery behavior

- API failure: retain attempt logs; do not create Temporary Input.
- Expected HK closure: record the date; do not create DTD.
- Missing intermediate HK trading date: stop before writing DTD.
- Duplicate confirmed date: reject the release; do not overwrite.
- Excel file lock: close the workbook and repeat the same date.
- Calculation failure: do not append Temporary Output.
- Rerun of an unchanged Temporary Input: report the existing row instead of duplicating it.

Output workbooks are saved through a temporary file and then replaced, reducing the risk of leaving a partially written workbook.

## 17 Known demonstration limitations

The demo uses Excel files rather than a transactional database, local identities rather than authenticated users, and a manually entered Checker name rather than role-based access control. Atomicity applies to each workbook replacement, not to a multi-system transaction. The replay dataset covers the supplied demonstration dates; other HK-open dates require LIVE mode or an additional saved source snapshot.

These limits are appropriate for a reviewable assignment demonstration. A deployed service would use a database, scheduler, secrets manager, authenticated roles, immutable event logs, monitoring and controlled source-data versioning.
