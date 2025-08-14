import pandas as pd
import numpy as np
import yfinance as yf
from datetime import timedelta
import time
import os
#home_dir = os.path.expanduser("~")
base_dir = os.path.expanduser('~/stonx1')
os.makedirs(base_dir,exist_ok=True)
# === SETTINGS ===
input_file = os.path.join(base_dir,"oip_mega_wreturns.csv")
output_file = os.path.join(base_dir,"oip_mega_wretvol.csv")
log_file = os.path.join(base_dir,"vol_calc.log")
lookbacks = [1, 5, 10, 15, 20, 35, 50, 75, 120, 180, 245]
checkpoint_every = 10  # save CSV every 10 rows
max_retries = 3
retry_delay = 3  # seconds

# === VOLATILITY FUNCTIONS ===
def close_to_close_vol(df):
    returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
    if len(returns) < 1:
        return np.nan
    return returns.std() * np.sqrt(252)

def garman_klass_vol(df):
    log_hl = np.log(df['High'] / df['Low'])
    log_co = np.log(df['Close'] / df['Open'])
    var = 0.5 * log_hl**2 - (2*np.log(2) - 1) * log_co**2
    return np.sqrt(var.mean()) * np.sqrt(252)

# === HELPER FUNCTIONS ===
def fetch_ohlcv_with_retry(ticker, start_date, end_date):
    for attempt in range(max_retries):
        try:
            df = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=False
            )
            if not df.empty:
                df.index = pd.to_datetime(df.index)
                return df
        except Exception:
            time.sleep(retry_delay * (attempt + 1))
    return pd.DataFrame()

def nearest_trading_day(date, trading_dates):
    if date in trading_dates:
        return date
    earlier_dates = trading_dates[trading_dates <= date]
    if not earlier_dates.empty:
        return earlier_dates.max()
    return None

# === LOAD CSV ===
df = pd.read_csv(input_file, parse_dates=['filing_date'])

# Create sig columns if they don't exist
for lb in lookbacks:
    for prefix in ['sig_c_', 'sig_gk_', 'sig_gkc_']:
        col = f"{prefix}{lb}"
        if col not in df.columns:
            df[col] = np.nan

# === PROCESS ROW BY ROW ===
for i, row in df.iterrows():
    ticker = row['ticker']
    filing_date = row['filing_date']

    if pd.isna(ticker) or pd.isna(filing_date):
        continue

    # Log starting
    with open(log_file, "a") as log:
        log.write(f"Starting row {i}, ticker {ticker}\n")

    # Compute the earliest date needed
    max_lb = max(lookbacks)
    start_date = filing_date - pd.tseries.offsets.BDay(max_lb)
    end_date = filing_date + timedelta(days=1)

    ohlcv = fetch_ohlcv_with_retry(ticker, start_date, end_date)
    if ohlcv.empty:
        with open(log_file, "a") as log:
            log.write(f"Failed download for ticker {ticker} at row {i}\n")
        continue

    trading_dates = pd.Series(ohlcv.index)
    nearest_date = nearest_trading_day(filing_date, trading_dates)
    if nearest_date is None:
        continue

    filing_idx = ohlcv.index.get_loc(nearest_date)

    for lb in lookbacks:
        start_idx = filing_idx - lb + 1
        if start_idx < 0:
            continue
        subdf = ohlcv.iloc[start_idx:filing_idx+1]
        if len(subdf) < 2:
            continue

        vol_c = close_to_close_vol(subdf)
        vol_gk = garman_klass_vol(subdf)
        vol_ratio = np.where(vol_c!=0, vol_gk / vol_c,np.nan)

        df.at[i, f"sig_c_{lb}"] = float(vol_c.iloc[0])
        df.at[i, f"sig_gk_{lb}"] = float(vol_gk.iloc[0])
        df.at[i, f"sig_gkc_{lb}"] = vol_ratio

    # Checkpoint: save every 10 rows
    if (i + 1) % checkpoint_every == 0:
        df.to_csv(output_file, index=False)
        with open(log_file, "a") as log:
            log.write(f"Checkpoint saved at row {i+1}\n")

# Final save
df.to_csv(output_file, index=False)
with open(log_file, "a") as log:
    log.write("Finished processing and saved final CSV.\n")


