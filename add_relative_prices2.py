import pandas as pd
import yfinance as yf
from tqdm import tqdm

def get_next_trading_day(trading_days, dt):
    """
    Return the first trading day strictly after dt.
    """
    idx = trading_days.searchsorted(dt, side='right')
    if idx >= len(trading_days):
        return None
    return trading_days[idx]

def get_exact_trading_day(trading_days, dt):
    """
    Return the trading day exactly matching dt, or None.
    """
    idx = trading_days.get_indexer([dt])
    if idx[0] == -1:
        return None
    return trading_days[idx[0]]

def add_prices_to_oip_precise(
        oip_df,
        ticker_col='ticker',
        filing_col='filing_date',
        fwindow=[1,2,5],
        bwindow=[1,2,5],
        price_col='Close',
        vol_col = 'Volume'
    ):
    """
    Adds filing price, mebuydate, mebuy price, and price columns at lookforward/back trading days from mebuydate.
    Returns (df_out, error_dict)
    """
    df = oip_df.copy()
    df[filing_col] = pd.to_datetime(df[filing_col], errors='coerce').dt.normalize()
    df['mebuydate'] = pd.NaT

    for n in fwindow:
        df[f'p_p{n}_td'] = None
        df[f'v_p{n}_td'] = None    # <-- NEW for volume
    for n in bwindow:
        df[f'p_m{n}_td'] = None
        df[f'v_m{n}_td'] = None    # <-- NEW for volume
    df['filing_price'] = None
    df['mebuy_price'] = None

    all_tickers = df[ticker_col].dropna().unique()
    price_data = {}
    vol_data = {}
    error_dict = {}

    # Download price data for each ticker
    for ticker in tqdm(all_tickers, desc="Downloading ticker prices"):
        try:
            # Determine earliest and latest date you will need
            min_filing = df[df[ticker_col] == ticker][filing_col].min()
            max_filing = df[df[ticker_col] == ticker][filing_col].max()
            # Conservative window to ensure all windows are covered
            start = min_filing - pd.Timedelta(days=max(bwindow)*2+10)
            end = max_filing + pd.Timedelta(days=max(fwindow)*2+10)
            hist = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            if price_col not in hist.columns or vol_col not in hist.columns:
                raise Exception(f"either '{vol_col}' and/or '{price_col}' column not found in price data")
            price_ser = hist[price_col].sort_index()
            vol_ser = hist[vol_col].sort_index()
            price_data[ticker] = (price_ser,vol_ser)
        except Exception as e:
            error_dict[ticker] = {'download_error': str(e)}
            price_data[ticker] = None

    # Add prices for each row
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Populating price data"):
        ticker = row[ticker_col]
        filing_date = row[filing_col]
        err = {}
        if ticker not in price_data or price_data[ticker] is None:
            err['ticker_not_found'] = True
            error_dict[ticker] = error_dict.get(ticker, {})
            error_dict[ticker][idx] = err
            continue
        price_ser,vol_ser = price_data[ticker]
        trading_days = price_ser.index

        # filing_price: get close ON filing_date if available
        fprice_date = get_exact_trading_day(trading_days, filing_date)
        if fprice_date is None:
            err['filing_price'] = f"Filing date {filing_date} not a trading day"
            df.at[idx, 'filing_price'] = None
        else:
            try:
                df.at[idx, 'filing_price'] = float(price_ser.loc[fprice_date])
            except Exception as e:
                err['filing_price'] = str(e)
                df.at[idx, 'filing_price'] = None

        # mebuydate: first trading day strictly after filing_date
        mebuydate = get_next_trading_day(trading_days, filing_date)
        if mebuydate is None:
            err['mebuydate'] = f"No trading day after {filing_date}"
            df.at[idx, 'mebuydate'] = pd.NaT
            df.at[idx, 'mebuy_price'] = None
            # skip relative price windows too, no anchor
            error_dict[ticker] = error_dict.get(ticker, {})
            error_dict[ticker][idx] = err
            continue
        else:
            df.at[idx, 'mebuydate'] = mebuydate

        # mebuy_price: close on mebuydate
        try:
            df.at[idx, 'mebuy_price'] = float(price_ser.loc[mebuydate])
        except Exception as e:
            err['mebuy_price'] = str(e)
            df.at[idx, 'mebuy_price'] = None

        # Now lookback/lookforward prices
        anchor_idx = trading_days.get_loc(mebuydate)
        # LookBACK
        for n in bwindow:
            if anchor_idx-n >= 0:
                try:
                    price = float(price_ser.iloc[anchor_idx-n].item())
                    volume = float(vol_ser.iloc[anchor_idx-n].item())
                    df.at[idx, f'p_m{n}_td'] = price
                    df.at[idx, f'v_m{n}_td'] = volume   # <-- NEW
                except Exception as e:
                    err[f'p_m{n}_td'] = str(e)
                    err[f'v_m{n}_td'] = str(e)          # <-- NEW
                    df.at[idx, f'p_m{n}_td'] = None
                    df.at[idx, f'v_m{n}_td'] = None     # <-- NEW
            else:
                err[f'p_m{n}_td'] = f"Not enough history for {n} trading days back"
                err[f'v_m{n}_td'] = f"Not enough history for {n} trading days back"
                df.at[idx, f'p_m{n}_td'] = None
                df.at[idx, f'v_m{n}_td'] = None
        # Lookforward
        for n in fwindow:
            if anchor_idx+n < len(price_ser):
                try:
                    price = float(price_ser.iloc[anchor_idx+n].item())
                    volume = float(vol_ser.iloc[anchor_idx+n].item())
                    df.at[idx, f'p_p{n}_td'] = price
                    df.at[idx, f'v_p{n}_td'] = volume   # <-- NEW
                except Exception as e:
                    err[f'p_p{n}_td'] = str(e)
                    err[f'v_p{n}_td'] = str(e)          # <-- NEW
                    df.at[idx, f'p_p{n}_td'] = None
                    df.at[idx, f'v_p{n}_td'] = None     # <-- NEW
            else:
                err[f'p_p{n}_td'] = f"Not enough future data for {n} trading days forward"
                err[f'v_p{n}_td'] = f"Not enough future data for {n} trading days forward"
                df.at[idx, f'p_p{n}_td'] = None
                df.at[idx, f'v_p{n}_td'] = None

        if err:
            error_dict[ticker] = error_dict.get(ticker, {})
            error_dict[ticker][idx] = err

    return df, error_dict

# ========== Example usage ==========

# oip_clean, error_dict = add_prices_to_oip_precise(oip, fwindow=[1,2,5], bwindow=[1,2,5])
# print(oip_clean.head())
# print(error_dict)
