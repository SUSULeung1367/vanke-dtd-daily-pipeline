"""Stable model, source and schema settings.

Change a value here only when the data contract or model policy changes.  Demo
dates and run mode belong in ``demo_settings.py`` instead.
"""

CHINA_TICKER = "000002.SZ"
HK_TICKER = "2202.HK"
FX_TICKER = "CNYHKD=X"
HKMA_URL = (
    "https://api.hkma.gov.hk/public/market-data-and-statistics/"
    "monthly-statistical-bulletin/efbn/efbn-yield-daily"
)

MAX_ATTEMPTS = 5
RETRY_DELAYS_SECONDS = [0, 1, 2, 4, 8]
REQUEST_TIMEOUT = (4, 8)

FX_MIN = 0.50
FX_MAX = 2.00
RISK_FREE_MIN = -5.00
RISK_FREE_MAX = 20.00
MAX_PRICE_CHANGE = 0.30
MAX_FX_CHANGE = 0.05
MAX_RISK_FREE_CHANGE_PP = 1.00
MAX_MARKET_CAP_CHANGE = 0.30

DTD_DELTA = 0.50
DTD_LOOKBACK_DAYS = 365
DTD_MIN_OBSERVATIONS = 50
DTD_TRADING_DAYS_PER_YEAR = 250

INPUT_COLUMNS = [
    "Comp_no",
    "Date",
    "CUR_MKT_CAP(HKD)",
    "BS_CUR_LIAB(HKD)",
    "BS_LT_BORROW(HKD)",
    "BS_TOT_LIAB2(HKD)",
    "BS_TOT_ASSET(HKD)",
    "Risk_Free_Rate",
]
BALANCE_SHEET_COLUMNS = [
    "BS_CUR_LIAB(HKD)",
    "BS_LT_BORROW(HKD)",
    "BS_TOT_LIAB2(HKD)",
    "BS_TOT_ASSET(HKD)",
]
DTD_OUTPUT_COLUMNS = ["Comp_no", "Date", "DTD"]
