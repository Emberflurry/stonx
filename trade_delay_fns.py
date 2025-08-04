import pandas as pd
import yfinance as yf
def add_trade_to_mebuy_delay(df, trade_date_col='trade_date', mebuy_date_col='mebuydate'):
    # Both cols should be pd.Timestamp (normalize if needed)
    df['trade_to_mebuy_days'] = (
        pd.to_datetime(df[mebuy_date_col]).dt.normalize() - 
        pd.to_datetime(df[trade_date_col]).dt.normalize()
    ).dt.days
    return df

def add_trade_to_mebuy_price_change(df, trade_price_col, mebuy_price_col='mebuy_price'):
    df['trade_to_mebuy_relpct'] = (
        df[mebuy_price_col] - df[trade_price_col]
    ) / df[trade_price_col]
    return df


def add_closeprice_at_insiderbuy(df, 
                                 ticker_col='ticker', 
                                 mebuydate_col='mebuydate', 
                                 trade_to_mebuy_days_col='trade_to_mebuy_days'):
    new_prices = []
    for i, row in df.iterrows():
        n = int(row[trade_to_mebuy_days_col])
        colname = f'p_m{n}_td'
        ticker = row[ticker_col]
        mebuydate = pd.to_datetime(row[mebuydate_col])
        # Calculate insider trade date
        insider_trade_date = mebuydate - pd.Timedelta(days=n)
        # 1. Try to use window column
        if colname in df.columns and pd.notnull(row.get(colname)):
            new_prices.append(row[colname])
        else:
            # 2. If not present, fetch from Yahoo
            try:
                import yfinance as yf
                price = yf.download(
                    ticker, 
                    start=insider_trade_date, 
                    end=insider_trade_date + pd.Timedelta(days=2), 
                    progress=False, 
                    auto_adjust=True
                )['Close']
                if insider_trade_date in price.index:
                    new_prices.append(float(price.loc[insider_trade_date]))
                elif len(price) > 0:
                    new_prices.append(float(price.iloc[0]))  # Use next available trading day
                else:
                    new_prices.append(float('nan'))
            except Exception as e:
                print(f"Failed for {ticker} on {insider_trade_date.date()}: {e}")
                new_prices.append(float('nan'))
    df['closeprice_at_insiderbuy'] = new_prices
    return df

