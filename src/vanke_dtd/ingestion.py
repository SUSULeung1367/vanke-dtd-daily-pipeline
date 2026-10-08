"""Daily input preparation orchestration.

This module coordinates source access, input QC and generated-workspace
persistence. It never writes the tracked baseline data under ``data/``.
"""

from __future__ import annotations

from datetime import datetime
import uuid

import pandas as pd

from .constants import BALANCE_SHEET_COLUMNS, CHINA_TICKER, FX_TICKER, HK_TICKER
from .quality import check_daily_data
from .sources import get_hkma_risk_free, get_online_close
from .store import read_excel_sheet_if_present, save_daily_datalog, update_temporary
from .workspace import configure_workspace, current_workspace


def configure_project(project_dir):
    """Compatibility alias for configuring one generated workspace."""
    return configure_workspace(project_dir).root


def process_daily_data(input_date, save_result=True):
    """Prepare one date, audit its sources and add only an eligible Temporary row."""
    paths = current_workspace()
    run_id, run_time = uuid.uuid4().hex, datetime.now()
    data_date = pd.to_datetime(str(input_date), format="%Y%m%d").normalize()
    calendar = pd.read_excel(paths.calendar, sheet_name="Daily Calendar")
    calendar["Date"] = pd.to_datetime(calendar["Date"]).dt.normalize()
    calendar_row = calendar.loc[calendar["Date"] == data_date]
    if calendar_row.empty:
        raise ValueError(f"{data_date.date()} is missing from Daily Calendar.")
    china_open = bool(calendar_row.iloc[0]["China_Open"])
    hk_open = bool(calendar_row.iloc[0]["HK_Open"])
    market_case = "BOTH_OPEN" if china_open and hk_open else "CHINA_ONLY" if china_open else "HK_ONLY" if hk_open else "BOTH_CLOSED"
    china = get_online_close("CHINA_CLOSE", CHINA_TICKER, data_date, require_exact=china_open)
    hk = get_online_close("HK_CLOSE", HK_TICKER, data_date, require_exact=hk_open)
    fx = get_online_close("FX", FX_TICKER, data_date, require_exact=hk_open)
    risk_free = get_hkma_risk_free(data_date, require_exact=hk_open, update_cache=save_result)
    sources = {"CHINA_CLOSE": china, "HK_CLOSE": hk, "FX": fx, "RISK_FREE": risk_free}

    capital = pd.read_excel(paths.issued_capital)
    capital["Time"] = pd.to_datetime(capital["Time"]).dt.normalize()
    capital = capital.loc[capital["Time"] <= data_date].sort_values("Time")
    if capital.empty:
        raise ValueError("No issued-capital data are available as of the input date.")
    capital_row = capital.iloc[-1]
    full_core = pd.read_excel(paths.confirmed_vanke, sheet_name="Input")
    full_core["Date"] = pd.to_datetime(full_core["Date"].astype(str), format="%Y%m%d")
    core = full_core.loc[full_core["Date"] <= data_date].sort_values("Date")
    if core.empty:
        raise ValueError("No balance-sheet data are available as of the input date.")
    core_row = core.iloc[-1]
    use_datalog = all(column in capital_row.index and pd.notna(capital_row[column]) for column in BALANCE_SHEET_COLUMNS)
    balance_sheet_row = capital_row if use_datalog else core_row
    balance_sheet_source_date = pd.Timestamp(capital_row["Time"] if use_datalog else core_row["Date"]).normalize()
    china_shares, hk_shares = float(capital_row["China Stock(A)"]), float(capital_row["HongKong Stock(H)"])
    if None not in (china["Value"], hk["Value"], fx["Value"]):
        china_market_cap = china["Value"] * china_shares * fx["Value"] / 1_000_000
        hk_market_cap = hk["Value"] * hk_shares / 1_000_000
        total_market_cap = china_market_cap + hk_market_cap
    else:
        china_market_cap = hk_market_cap = total_market_cap = None
    confirmed_previous = full_core.loc[full_core["Date"] < data_date, ["Date", "CUR_MKT_CAP(HKD)"]].copy()
    confirmed_previous["_source_priority"] = 2
    previous_frames = [confirmed_previous]
    temporary = read_excel_sheet_if_present(paths.temporary_input, "Input")
    if not temporary.empty:
        temporary["Date"] = pd.to_datetime(temporary["Date"].astype(str).str.replace(r"\.0$", "", regex=True), format="%Y%m%d")
        temporary = temporary.loc[temporary["Date"] < data_date, ["Date", "CUR_MKT_CAP(HKD)"]].copy()
        temporary["_source_priority"] = 1
        previous_frames.append(temporary)
    previous = pd.concat(previous_frames, ignore_index=True).sort_values(["Date", "_source_priority"]).drop_duplicates("Date", keep="last").sort_values("Date")
    previous_market_cap = float(previous.iloc[-1]["CUR_MKT_CAP(HKD)"]) if not previous.empty else None
    record = {
        "Run_ID": run_id, "Run_Time": run_time, "Comp_no": int(core_row["Comp_no"]), "Date": data_date,
        "China_Open": china_open, "HK_Open": hk_open, "Market_Case": market_case,
        "China_Close": china["Value"] if china_open else None, "China_Close_Used": china["Value"],
        "China_Close_Source_Date": china["Source_Date"], "China_API_Status": china["Status"], "China_API_Attempts": len(china["Attempts"]),
        "HK_Close": hk["Value"] if hk_open else None, "HK_Close_Used": hk["Value"],
        "HK_Close_Source_Date": hk["Source_Date"], "HK_API_Status": hk["Status"], "HK_API_Attempts": len(hk["Attempts"]),
        "FX_Rate": fx["Value"], "FX_Source_Date": fx["Source_Date"], "FX_API_Status": fx["Status"], "FX_API_Attempts": len(fx["Attempts"]),
        "Risk_Free_Rate": risk_free["Value"], "Risk_Free_Source_Date": risk_free["Source_Date"],
        "Risk_Free_API_Status": risk_free["Status"], "Risk_Free_API_Attempts": len(risk_free["Attempts"]),
        "China_Shares": china_shares, "HK_Shares": hk_shares, "Capital_Source_Date": pd.Timestamp(capital_row["Time"]).normalize(),
        "China_Market_Cap_HKD_mn": china_market_cap, "HK_Market_Cap_HKD_mn": hk_market_cap,
        "CUR_MKT_CAP(HKD)": total_market_cap, "Previous_CUR_MKT_CAP(HKD)": previous_market_cap,
        "Balance_Sheet_Source_Date": balance_sheet_source_date,
    }
    for column in BALANCE_SHEET_COLUMNS:
        record[column] = float(balance_sheet_row[column])
    record.update(check_daily_data(record, sources))
    temporary_action, conflict = update_temporary(record, save_result)
    if conflict:
        record["Bug_Flag"] = True
        record["Bug_Message"] = " | ".join(item for item in [record["Bug_Message"], "New values conflict with an existing approved Temporary row."] if item)
        record["Quality_Status"], record["Ready_For_DTD"] = "FAIL", False
    record["Temporary_Action"] = temporary_action
    attempts = [{"Run_ID": run_id, "Input_Date": data_date, **attempt} for source in sources.values() for attempt in source["Attempts"]]
    if save_result:
        save_daily_datalog(record, attempts)
    if record["Bug_Flag"] or record["Review_Flag"]:
        saved = "Daily Datalog was saved." if save_result else "Dry run; no file was changed."
        raise RuntimeError(f"ALERT: data did not pass the Temporary gate. {saved} Temporary was not updated. Bug={record['Bug_Message']} Review={record['Review_Message']}")
    return pd.DataFrame([record])
