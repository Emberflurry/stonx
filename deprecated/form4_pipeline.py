#FAILED/DEPRECATED
# form4_pipeline.py

import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import time
from pandas.tseries.offsets import BDay
import yfinance as yf

BASE_URL = "https://www.sec.gov/"
HEADERS = {'User-Agent': 'Your Name your_email@example.com'}  # Replace with real name/email per SEC guidance

# SEC CIK lookup table (symbol to CIK)
def load_cik_map():
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    cik_map = {
        v['ticker'].upper(): str(v['cik_str']).zfill(10)
        for v in data.values()
    }
    return cik_map

# Get Form 4 filings for a specific CIK over the past N days
def get_recent_form4s(cik, days_back=30):
    base_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(base_url, headers=HEADERS)
    if r.status_code != 200:
        return None
    filings = r.json().get("filings", {}).get("recent", {})
    df = pd.DataFrame(filings)
    df = df[df['form'] == '4']
    df['filingDate'] = pd.to_datetime(df['filingDate'], utc=True)
    df = df[df['filingDate'] > (datetime.now(timezone.utc) - timedelta(days=days_back))]
    df['accession_url'] = df['accessionNumber'].apply(
        lambda x: f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{x.replace('-', '')}/{x}-index.htm")
    return df[['accessionNumber', 'filingDate', 'accession_url']]

# Example run for a few tickers
def batch_fetch_form4s(tickers):
    cik_map = load_cik_map()
    output = []
    for ticker in tickers:
        cik = cik_map.get(ticker.upper())
        if not cik:
            continue
        print(f"Fetching Form 4s for {ticker} (CIK {cik})")
        df = get_recent_form4s(cik)
        if df is not None and not df.empty:
            df['ticker'] = ticker
            output.append(df)
        time.sleep(0.5)
    return pd.concat(output) if output else pd.DataFrame()

# Pull price data using yfinance
def fetch_price_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

# Merge form4 events with forward price performance
def attach_forward_returns(df_form4s, window=30):
    result_rows = []
    for ticker in df_form4s['ticker'].unique():
        df_ticker = df_form4s[df_form4s['ticker'] == ticker]
        min_date = df_ticker['filingDate'].min().date() - timedelta(days=1)
        max_date = df_ticker['filingDate'].max().date() + timedelta(days=window+2)
        price_df = fetch_price_data(ticker, min_date, max_date)
        if price_df.empty:
            continue
        price_df = price_df[['Close']].rename(columns={'Close': 'close'})
        price_df.index = pd.to_datetime(price_df.index)

        for _, row in df_ticker.iterrows():
            event_date = row['filingDate'].date()
            try:
                event_ts = price_df.index[price_df.index.get_indexer([pd.Timestamp(event_date)], method='nearest')[0]]
                fwd_ts = event_ts + BDay(window)
                if fwd_ts not in price_df.index:
                    continue
                start_price = price_df.loc[event_ts, 'close']
                fwd_price = price_df.loc[fwd_ts, 'close']
                fwd_return = (fwd_price - start_price) / start_price
                result_rows.append({
                    'ticker': ticker,
                    'filingDate': row['filingDate'].date(),
                    'start_price': start_price,
                    'fwd_price': fwd_price,
                    'fwd_return': fwd_return
                })
            except Exception as e:
                print(f"Failed for {ticker} on {event_date}: {e}")
                continue
    return pd.DataFrame(result_rows)

if __name__ == '__main__':
    tickers = ['AAPL', 'TSLA', 'NVDA', 'META']  # Replace or expand
    df_form4s = batch_fetch_form4s(tickers)
    print(df_form4s.head())

    df_returns = attach_forward_returns(df_form4s, window=10)
    print("\nForward Return Samples:")
    print(df_returns.head())
