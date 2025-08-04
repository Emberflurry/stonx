import pandas as pd
import numpy as np
import yfinance as yf
#from tqdm import tqdm
#from sklearn.ensemble import RandomForestRegressor
#from sklearn.metrics import mean_squared_error, r2_score
import unicodedata

def clean_col(col):
    col = str(col)
    col = col.replace('\xa0', ' ')      # Replace non-breaking spaces
    col = col.strip()
    col = col.lower()
    col = unicodedata.normalize('NFKD', col)
    return col



def get_oip_1p(url):
    url = url
    tables = pd.read_html(url)
    df = tables[11]
    df.columns = [clean_col(c) for c in df.columns]
    df = df.rename(columns={'δown': 'deltaown'})
    for c in df.columns:
        if 'own' in c and ('δ' in c or 'Δ' in c):
            df = df.rename(columns={c: 'deltaown'})


    print(df.columns.tolist())
    if 'Î´own' in df.columns:
        df = df.rename(columns={'Î´own': 'deltaown'})
    elif 'δown' in df.columns:
        df = df.rename(columns={'δown': 'deltaown'})
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
    df['d_own_plus%_isnew'] = (df['deltaown'].isnull() | (df['deltaown'] == 'New')).astype(int)
    df["d_own_plus%"] = (
    df["deltaown"]
    .replace("New", 999) #new insider purchases get 999 value...hopefully works
    .replace(r'>', '', regex=True)          # remove '>' character
    .replace(r'[\+,%]', '', regex=True)     # remove '+', ',', '%'
    .astype(float)
    )
    
    df['value'] = df['value'].replace(r'[+\$,]', '', regex=True).astype(float)
    #drop the price column
    df = df.drop(columns=['price','deltaown'])

    return df