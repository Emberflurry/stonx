#MAIN
#get market pricing for insider trade date data
import yfinance as yf
import pandas as pd
def add_prices_to_oip(oip_df):
    failedtickers = []
    failed_dict = {}
    df = oip_df.copy()
    df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
    df['mebuydate'] = pd.to_datetime(df['mebuydate'], errors='coerce')
    
    df['filing_price'] = None
    df['mebuy_price'] = None
    
    for ticker in df['ticker'].unique():
        try:
            df_ticker = df[df['ticker'] == ticker]
            min_date = df_ticker[['filing_date', 'mebuydate']].min().min() - pd.Timedelta(days=5)
            max_date = df_ticker[['filing_date', 'mebuydate']].max().max() + pd.Timedelta(days=5)
            hist = yf.download(ticker, start=min_date, end=max_date, progress=False,auto_adjust=True)['Close']
            hist.index = pd.to_datetime(hist.index)
        except Exception as e:
            print(f"Failed to fetch price data for {ticker}: {e}")
            failedtickers.append(ticker)
            innerdict = {'lvl': 'yfdload1','min_date':min_date, 'max_date':max_date,
                         'company_name': df.loc[df['ticker'] == ticker, 'company_name'].iloc[0] ,'error': str(e)}
            failed_dict[ticker] = innerdict
            continue

        for idx, row in df[df['ticker'] == ticker].iterrows():
            # Filing price
            try:
                fdate = row['filing_date']
                fprice_date = hist.index[hist.index.get_indexer([fdate], method='nearest')[0] -1]
                #off by ONE day again, need to subtract 1. lol. bruh
                df.at[idx, 'filing_price'] = hist.loc[fprice_date].iloc[0]
            except Exception as e:
                df.at[idx, 'filing_price'] = None
                failedtickers.append(ticker)
                innerdict = {'lvl': 'iterfilingprice2','fdate':fdate, 'fprice_date':fprice_date,
                            'company_name': df.loc[df['ticker'] == ticker, 'company_name'].iloc[0] ,'error': str(e)}
                failed_dict[ticker] = innerdict
            # Me-buy price
            try:
                mdate = row['mebuydate']
                mprice_date = hist.index[hist.index.get_indexer([mdate], method='nearest')[0] -1]
                #^minus one because it seems to shift 1d too far forward for some reason. manually checked ag yf
                df.at[idx,'mebuy_pricedateQ'] = mprice_date
                df.at[idx, 'mebuy_price'] = hist.loc[mprice_date].iloc[0]
            except Exception as e:
                df.at[idx, 'mebuy_price'] = None
                failedtickers.append(ticker)
                innerdict = {'lvl': 'itermebuyprice2','mdate':mdate, 'mprice_date':mprice_date,
                            'company_name': df.loc[df['ticker'] == ticker, 'company_name'].iloc[0] ,'error': str(e)}
                failed_dict[ticker] = innerdict

    return df,failedtickers,failed_dict
# oip_with_prices,failedtickers = add_prices_to_oip(oip)
# failedtickersunique = list(set(failedtickers))