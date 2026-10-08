"""Input quality controls for daily market observations."""

from __future__ import annotations

import pandas as pd

from .pipeline_config import (
    BALANCE_SHEET_COLUMNS, FX_MAX, FX_MIN, MAX_FX_CHANGE,
    MAX_MARKET_CAP_CHANGE, MAX_PRICE_CHANGE, MAX_RISK_FREE_CHANGE_PP,
    RISK_FREE_MAX, RISK_FREE_MIN,
)


def percentage_change(current, previous):
    if current is None or previous in (None, 0) or pd.isna(previous):
        return None
    return abs(float(current) / float(previous) - 1)


def check_daily_data(record, sources):
    """Return blocking bugs, warnings, review flags and DTD eligibility."""
    bugs, warnings_list, review_items = [], [], []
    china, hk = sources["CHINA_CLOSE"], sources["HK_CLOSE"]
    fx, risk_free = sources["FX"], sources["RISK_FREE"]
    data_date = record["Date"]
    for label, source in (("China Close", china), ("HK Close", hk), ("FX", fx)):
        if not source["OK"]:
            bugs.append(f"{label} invalid: {source['Status']} {source['Error']}")
    if record["HK_Open"] and not risk_free["OK"]:
        bugs.append(f"Exact HKMA risk-free rate unavailable: {risk_free['Status']}")
    if record["China_Open"] and china["Source_Date"] != data_date:
        bugs.append("China market is open but China Close is not exact-date.")
    if record["HK_Open"] and hk["Source_Date"] != data_date:
        bugs.append("HK market is open but HK Close is not exact-date.")
    if record["HK_Open"] and fx["Source_Date"] != data_date:
        bugs.append("HK production date requires an exact-date FX observation.")
    if record["HK_Open"] and risk_free["Source_Date"] != data_date:
        bugs.append("HK production date requires an exact-date risk-free rate.")
    if not record["China_Open"] and china["Value"] is not None:
        warnings_list.append(f"China closed; carried Close from {china['Source_Date'].date()}.")
    if not record["HK_Open"] and hk["Value"] is not None:
        warnings_list.append(f"HK closed; carried Close from {hk['Source_Date'].date()}.")
    if not record["HK_Open"] and risk_free["Source_Date"] is not None:
        warnings_list.append(f"HK closed; carried risk-free rate from {risk_free['Source_Date'].date()}.")
    for name, source in sources.items():
        failed = sum(row["Attempt_Status"] == "FAILED" for row in source["Attempts"])
        if failed and source["OK"]:
            warnings_list.append(f"{name} succeeded after {failed} failed attempt(s).")
    for label in ["China_Close_Used", "HK_Close_Used", "FX_Rate"]:
        value = record.get(label)
        if value is None or pd.isna(value) or float(value) <= 0:
            bugs.append(f"{label} must be present and positive.")
    if record["FX_Rate"] is not None and not FX_MIN <= record["FX_Rate"] <= FX_MAX:
        bugs.append(f"FX_Rate outside [{FX_MIN}, {FX_MAX}].")
    if record["Risk_Free_Rate"] is not None and not RISK_FREE_MIN <= record["Risk_Free_Rate"] <= RISK_FREE_MAX:
        bugs.append("Risk_Free_Rate is outside the plausible range.")
    for label in ["China_Shares", "HK_Shares", *BALANCE_SHEET_COLUMNS]:
        value = record.get(label)
        if value is None or pd.isna(value) or float(value) <= 0:
            bugs.append(f"{label} must be present and positive.")
    if record["CUR_MKT_CAP(HKD)"] is None or record["CUR_MKT_CAP(HKD)"] <= 0:
        bugs.append("CUR_MKT_CAP(HKD) must be present and positive.")
    changes = {
        "China Close": percentage_change(china["Value"], china["Previous_Value"]),
        "HK Close": percentage_change(hk["Value"], hk["Previous_Value"]),
        "FX": percentage_change(fx["Value"], fx["Previous_Value"]),
    }
    if changes["China Close"] is not None and changes["China Close"] > MAX_PRICE_CHANGE:
        review_items.append(f"China Close change {changes['China Close']:.1%}.")
    if changes["HK Close"] is not None and changes["HK Close"] > MAX_PRICE_CHANGE:
        review_items.append(f"HK Close change {changes['HK Close']:.1%}.")
    if changes["FX"] is not None and changes["FX"] > MAX_FX_CHANGE:
        review_items.append(f"FX change {changes['FX']:.1%}.")
    if risk_free["Value"] is not None and risk_free["Previous_Value"] is not None:
        change = abs(risk_free["Value"] - risk_free["Previous_Value"])
        if change > MAX_RISK_FREE_CHANGE_PP:
            review_items.append(f"Risk-free change {change:.2f} percentage points.")
    market_cap_change = percentage_change(record["CUR_MKT_CAP(HKD)"], record.get("Previous_CUR_MKT_CAP(HKD)"))
    if market_cap_change is not None and market_cap_change > MAX_MARKET_CAP_CHANGE:
        review_items.append(f"Market-cap change {market_cap_change:.1%}.")
    quality_status = "FAIL" if bugs else "REVIEW_REQUIRED" if review_items else "PASS_WITH_WARNING" if warnings_list else "PASS"
    return {
        "Bug_Flag": bool(bugs), "Bug_Message": " | ".join(bugs) if bugs else None,
        "Warning_Flag": bool(warnings_list), "Warning_Message": " | ".join(warnings_list) if warnings_list else None,
        "Review_Flag": bool(review_items), "Review_Message": " | ".join(review_items) if review_items else None,
        "Quality_Status": quality_status,
        "Ready_For_DTD": record["HK_Open"] and quality_status in {"PASS", "PASS_WITH_WARNING"},
    }
