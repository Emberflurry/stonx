import pandas as pd
import numpy as np
import yfinance as yf
#from tqdm import tqdm
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.metrics import mean_squared_error, r2_score


def get_oip_1p(url):
    url = url
    tables = pd.read_html(url)
    df = tables[11]
    df.columns = (
    pd.Index(df.columns.map(str))
    .str.replace(r'\s+', '_', regex=True)  # replaces spaces, \xa0, tabs, etc.
    .str.strip()
    .str.lower() )

    df.columns = pd.Index(df.columns.map(str)).str.replace(' ', '_', regex=True)
    df = df[df["trade_type"].str.contains("Purchase", na=False)]
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors='coerce')
    df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
    #set mebuydate = filing_date + 1 day
    #df["mebuydate"] = df["filing_date"] + pd.Timedelta(days=1) #NO!!!! BAD - need stricter way of getting next TRADING DAY
    df["insider_price"] = df["price"].replace('[$,]', '', regex=True).astype(float)
    df["qty"] = df["qty"].replace('[+,]', '', regex=True).astype(int)
    df["d_own_plus%"] = (
    df["δown"]
    .replace("New", np.nan)
    .replace(r'>', '', regex=True)          # remove '>' character
    .replace(r'[\+,%]', '', regex=True)     # remove '+', ',', '%'
    .astype(float)
)
    df['value'] = df['value'].replace(r'[+\$,]', '', regex=True).astype(float)
    #drop the price column
    df = df.drop(columns=['price'])

    return df