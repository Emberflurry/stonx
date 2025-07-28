#adding market prices around insider dates
from tqdm import tqdm
import pandas as pd
import yfinance as yf
def add_relative_prices(df, mebuy_col='mebuydate', ticker_col='ticker',windows=[1, 2, 3, 4, 5, 6, 10, 25, 50, 75, 125, 175, 225]):
    # Define trading day offsets (negative = past, positive = future)
    offsets = windows
    past_cols = [f'p_m{n}_td' for n in offsets]
    future_cols = [f'p_p{n}_td' for n in offsets]

    # Prepare output DataFrame
    df_out = df.copy()
    for col in past_cols + future_cols:
        df_out[col] = None

    # Unique tickers to avoid redundant downloads
    all_tickers = df[ticker_col].dropna().unique()
    ticker_price_data = {}

    # Download price data for each ticker
    for ticker in tqdm(all_tickers, desc="Downloading price data"):
        min_date = df[df[ticker_col] == ticker][mebuy_col].min() - pd.Timedelta(days=500)
        max_date = df[df[ticker_col] == ticker][mebuy_col].max() + pd.Timedelta(days=500)
        try:
            hist = yf.download(ticker, start=min_date, end=max_date, progress=False)['Close']
            hist = hist.sort_index()
            ticker_price_data[ticker] = hist
        except Exception as e:
            print(f"Failed to download {ticker}: {e}")

    # Loop over rows and extract past/future prices relative to mebuydate
    for i, row in tqdm(df_out.iterrows(), total=len(df_out), desc="Extracting prices"):
        ticker = row[ticker_col]
        mebuy_date = pd.to_datetime(row[mebuy_col], errors='coerce')
        if pd.isna(mebuy_date) or ticker not in ticker_price_data:
            continue

        price_series = ticker_price_data[ticker]
        if mebuy_date not in price_series.index:
            # Get closest trading day if not found
            try:
                mebuy_date = price_series.index[price_series.index.get_indexer([mebuy_date], method='nearest')[0]]
            except:
                continue

        try:
            idx = price_series.index.get_loc(mebuy_date)
        except KeyError:
            continue

        for offset in offsets:
            # Past
            if idx - offset >= 0:
                past_price = price_series.iloc[idx - offset]
                df_out.at[i, f'p_m{offset}_td'] = past_price.item()

            # Future
            if idx + offset < len(price_series):
                future_price = price_series.iloc[idx + offset]
                df_out.at[i, f'p_p{offset}_td'] = future_price.item()

    return df_out
#run
# oip_with_prices_relative = add_relative_prices(oip_clean)
# print(oip_with_prices_relative.head(1))
# print(oip_with_prices_relative.columns)