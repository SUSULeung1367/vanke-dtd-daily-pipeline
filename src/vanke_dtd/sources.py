"""External market-data access and the local HKMA rate cache."""

from __future__ import annotations

from datetime import datetime
import time

import pandas as pd
import requests
import yfinance as yf

from .constants import HKMA_URL, MAX_ATTEMPTS, REQUEST_TIMEOUT, RETRY_DELAYS_SECONDS
from .workspace import current_workspace


def run_with_retry(source_name, data_date, fetch_once):
    """Run one source request with bounded retries and auditable attempts."""
    attempts = []
    last_error = None
    for attempt_number in range(1, MAX_ATTEMPTS + 1):
        delay = RETRY_DELAYS_SECONDS[attempt_number - 1]
        if delay:
            time.sleep(delay)
        started_at = datetime.now()
        try:
            value = fetch_once()
            attempts.append({
                "API": source_name, "Attempt": attempt_number,
                "Attempt_Status": "SUCCESS", "Attempt_Time": started_at,
                "Error_Type": None, "Error_Message": None,
            })
            return value, attempts, None
        except Exception as error:  # Source errors are audit data, not silent fallbacks.
            last_error = error
            attempts.append({
                "API": source_name, "Attempt": attempt_number,
                "Attempt_Status": "FAILED", "Attempt_Time": started_at,
                "Error_Type": type(error).__name__, "Error_Message": str(error)[:500],
            })
    return None, attempts, last_error


def _extract_close_series(downloaded, ticker):
    close = downloaded["Close"]
    if isinstance(close, pd.DataFrame):
        close = close[ticker] if ticker in close.columns else close.iloc[:, 0]
    close.index = pd.to_datetime(close.index)
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    close.index = close.index.normalize()
    return pd.to_numeric(close, errors="coerce").dropna().sort_index()


def get_online_close(source_name, ticker, data_date, require_exact):
    """Get the latest close on or before a date and record its source date."""
    data_date = pd.Timestamp(data_date).normalize()

    def fetch_once():
        downloaded = yf.download(
            ticker,
            start=(data_date - pd.Timedelta(days=20)).strftime("%Y-%m-%d"),
            end=(data_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            auto_adjust=False, progress=False, threads=False,
            timeout=REQUEST_TIMEOUT[1],
        )
        if downloaded.empty:
            raise ValueError(f"No online data returned for {ticker}.")
        close = _extract_close_series(downloaded, ticker)
        available = close.loc[close.index <= data_date]
        if available.empty:
            raise ValueError(f"No Close exists on or before {data_date.date()}.")
        source_date = pd.Timestamp(available.index[-1]).normalize()
        previous = available.iloc[:-1]
        return {
            "Value": float(available.iloc[-1]), "Source_Date": source_date,
            "Previous_Value": float(previous.iloc[-1]) if not previous.empty else None,
            "Previous_Source_Date": (
                pd.Timestamp(previous.index[-1]).normalize() if not previous.empty else None
            ),
        }

    payload, attempts, error = run_with_retry(source_name, data_date, fetch_once)
    if payload is None:
        return {
            "OK": False, "Value": None, "Source_Date": None,
            "Previous_Value": None, "Previous_Source_Date": None,
            "Exact_Required": require_exact,
            "Status": f"FAILED_AFTER_{MAX_ATTEMPTS}_ATTEMPTS",
            "Error": str(error), "Attempts": attempts,
        }
    exact_match = payload["Source_Date"] == data_date
    return {
        "OK": (not require_exact) or exact_match, **payload,
        "Exact_Required": require_exact,
        "Status": "ONLINE_EXACT" if exact_match else "ONLINE_ASOF_PRIOR_DATE",
        "Error": None if ((not require_exact) or exact_match) else "Source date mismatch",
        "Attempts": attempts,
    }


def load_risk_free_cache():
    path = current_workspace().risk_free_cache
    if not path.exists():
        return pd.DataFrame(columns=["Date", "Day", "Risk_Free_Rate", "Risk_Free_Decimal"])
    cache = pd.read_excel(path)
    if cache.empty:
        return cache
    cache["Date"] = pd.to_datetime(cache["Date"]).dt.normalize()
    cache["Risk_Free_Rate"] = pd.to_numeric(cache["Risk_Free_Rate"], errors="coerce")
    return cache.dropna(subset=["Date", "Risk_Free_Rate"])


def save_risk_free_cache(cache, data_date, value):
    """Append one live exact-date rate to the generated workspace cache."""
    new_row = pd.DataFrame([{
        "Date": data_date, "Day": pd.Timestamp(data_date).day_name(),
        "Risk_Free_Rate": float(value), "Risk_Free_Decimal": float(value) / 100,
    }])
    updated = pd.concat([cache, new_row], ignore_index=True)
    updated["Date"] = pd.to_datetime(updated["Date"]).dt.normalize()
    updated = updated.sort_values("Date").drop_duplicates("Date", keep="last").reset_index(drop=True)
    updated.to_excel(current_workspace().risk_free_cache, index=False)


def get_hkma_risk_free(data_date, require_exact, update_cache):
    """Use an exact cached/online rate for an eligible HK production day."""
    data_date = pd.Timestamp(data_date).normalize()
    cache = load_risk_free_cache()
    available = cache.loc[cache["Date"] <= data_date].sort_values("Date")
    exact = available.loc[available["Date"] == data_date]
    previous = available.loc[available["Date"] < data_date]
    previous_value = float(previous.iloc[-1]["Risk_Free_Rate"]) if not previous.empty else None
    if not exact.empty:
        row = exact.iloc[-1]
        return {
            "OK": True, "Value": float(row["Risk_Free_Rate"]),
            "Source_Date": pd.Timestamp(row["Date"]).normalize(),
            "Previous_Value": previous_value, "Status": "LOCAL_CACHE_EXACT",
            "Error": None, "Attempts": [{
                "API": "HKMA_RISK_FREE", "Attempt": 0, "Attempt_Status": "CACHE_HIT",
                "Attempt_Time": datetime.now(), "Error_Type": None, "Error_Message": None,
            }],
        }
    if not require_exact:
        if available.empty:
            return {
                "OK": False, "Value": None, "Source_Date": None,
                "Previous_Value": None, "Status": "NO_CACHED_ASOF_VALUE",
                "Error": "No cached HKMA value", "Attempts": [],
            }
        row = available.iloc[-1]
        return {
            "OK": True, "Value": float(row["Risk_Free_Rate"]),
            "Source_Date": pd.Timestamp(row["Date"]).normalize(),
            "Previous_Value": previous_value, "Status": "LOCAL_CACHE_ASOF_CLOSED_DAY",
            "Error": None, "Attempts": [],
        }

    def fetch_once():
        response = requests.get(
            HKMA_URL,
            params={"choose": "end_of_day", "from": data_date.strftime("%Y-%m-%d"),
                    "to": data_date.strftime("%Y-%m-%d"),
                    "fields": "end_of_day,efb_364d", "pagesize": 5},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("header", {}).get("success", False):
            raise ValueError(f"HKMA API error: {payload.get('header')}")
        online = pd.DataFrame(payload.get("result", {}).get("records", []))
        if online.empty:
            raise ValueError("HKMA returned no exact-date record.")
        online["Date"] = pd.to_datetime(online["end_of_day"])
        online["Value"] = pd.to_numeric(online["efb_364d"], errors="coerce")
        online = online.dropna(subset=["Date", "Value"])
        online = online.loc[online["Date"] == data_date]
        if online.empty:
            raise ValueError("HKMA returned no usable exact-date yield.")
        return float(online.iloc[-1]["Value"])

    value, attempts, error = run_with_retry("HKMA_RISK_FREE", data_date, fetch_once)
    if value is not None:
        if update_cache:
            save_risk_free_cache(cache, data_date, value)
        return {
            "OK": True, "Value": value, "Source_Date": data_date,
            "Previous_Value": previous_value,
            "Status": "ONLINE_EXACT_AND_CACHED" if update_cache else "ONLINE_EXACT_DRY_RUN",
            "Error": None, "Attempts": attempts,
        }
    fallback_value = float(available.iloc[-1]["Risk_Free_Rate"]) if not available.empty else None
    fallback_date = pd.Timestamp(available.iloc[-1]["Date"]).normalize() if not available.empty else None
    return {
        "OK": False, "Value": fallback_value, "Source_Date": fallback_date,
        "Previous_Value": previous_value,
        "Status": f"FAILED_AFTER_{MAX_ATTEMPTS}_ATTEMPTS_STALE_CACHE_ONLY",
        "Error": str(error), "Attempts": attempts,
    }
