import pandas as pd
def add_trade_to_mebuy_delay(df, trade_date_col='trade_date', mebuy_date_col='mebuydate'):
    # Both cols should be pd.Timestamp (normalize if needed)
    df['trade_to_mebuy_days'] = (
        pd.to_datetime(df[mebuy_date_col]).dt.normalize() - 
        pd.to_datetime(df[trade_date_col]).dt.normalize()
    ).dt.days
    return df

def add_trade_to_mebuy_price_change(df, trade_price_col='trade_price', mebuy_price_col='mebuy_price'):
    df['trade_to_mebuy_relpct'] = (
        df[mebuy_price_col] - df[trade_price_col]
    ) / df[trade_price_col]
    return df


def add_closeprice_at_insiderbuy(df, mebuydate_col='mebuydate', trade_to_mebuy_days_col='trade_to_mebuy_days'):
    # Find which lookback col to use for each row
    new_prices = []
    for i, row in df.iterrows():
        n = int(row[trade_to_mebuy_days_col])
        # Example: if n == 4, look for 'p_m4_td'
        colname = f'p_m{n}_td'
        if colname in df.columns and pd.notnull(row[colname]):
            new_prices.append(row[colname])
        else:
            new_prices.append(float('nan'))
    df['closeprice_at_insiderbuy'] = new_prices
    return df

