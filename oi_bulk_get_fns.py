from urllib.parse import urlencode, quote_plus
from get_oip_1p import *
import importlib
#import add_relative_prices2
import get_oip_1p
#importlib.reload(add_relative_prices2)
importlib.reload(get_oip_1p)
from get_oip_1p import *
def openinsider_url(start_date, end_date, count=1000, page=1):
    """
    page shouldnt matter, it downloads the full data. 
    start_date, end_date: pd.Timestamp or 'MM/DD/YYYY' string
    """
    # Format dates as MM/DD/YYYY
    def fmt(d):
        if isinstance(d, str):
            return d
        return d.strftime("%m/%d/%Y")
    
    # Build fdr string: MM/DD/YYYY+-+MM/DD/YYYY, url-encoded
    fdr = f"{fmt(start_date)} - {fmt(end_date)}"
    fdr_encoded = quote_plus(fdr)  # this will encode as "05%2F01%2F2022+-+05%2F01%2F2023"

    base_url = "http://openinsider.com/screener?"

    params = {
        "s": "",
        "o": "",
        "pl": "",
        "ph": "",
        "ll": "",
        "lh": "",
        "fd": "-1",
        "fdr": fdr_encoded,  # already encoded
        "td": "0",
        "tdr": "",
        "fdlyl": "",
        "fdlyh": "",
        "daysago": "",
        "xp": "1",
        "vl": "",
        "vh": "",
        "ocl": "",
        "och": "",
        "sic1": "-1",
        "sicl": "100",
        "sich": "9999",
        "grp": "0",
        "nfl": "",
        "nfh": "",
        "nil": "",
        "nih": "",
        "nol": "",
        "noh": "",
        "v2l": "",
        "v2h": "",
        "oc2l": "",
        "oc2h": "",
        "sortcol": "0",
        "cnt": str(count),
        "page": str(page),
    }

    # Remove fdr from params so we can append the encoded one at the end
    params.pop("fdr")
    url = base_url + urlencode(params) + f"&fdr={fdr_encoded}"
    return url
# Example usage:
url = openinsider_url("05/01/2022", "05/10/2023",count=1000,page=1)
#print(url)
#works


from datetime import timedelta
import pandas as pd

def get_all_openinsider_chunks(
    start,
    end,
    chunk_size=1000,
    window_days=25,
    overlap_days=0
):
    all_chunks = []
    current_end = end

    while current_end > start:
        print(f"Fetching: {current_end.date()} back to {start.date()}")
        url = openinsider_url(start-timedelta(days=1), current_end, chunk_size)
        df = get_oip_1p(url)

        if df.empty:
            print(f"No data found for {start.date()} to {current_end.date()}. Stopping.")
            break
        all_chunks.append(df)

        earliest = df['filing_date'].min()
        # Next window ends at earliest + overlap_days (never before start)
        current_end = earliest + timedelta(days=overlap_days)
        print(f"Next window ends at {current_end.date()} (overlap from {earliest.date()})")
        # Save progress
        filename = f"oi_rawpull_ymd_{start.strftime('%Y_%m_%d')}_{end.strftime('%Y_%m_%d')}_incl.csv"
        pd.concat(all_chunks).to_csv(filename, index=False)

    all_df = pd.concat(all_chunks, ignore_index=True)
    all_df = all_df.drop_duplicates(subset=[
        'ticker', 'filing_date', 'trade_date', 'insider_name',
        'qty', 'owned', 'value', 'insider_price', 'd_own_plus%'
    ])
    return all_df

# Usage:
#start = pd.Timestamp('2019-01-01')
#end = pd.Timestamp('2025-08-06')
# all_openinsider = get_all_openinsider_chunks(start, end, 
#                                              chunk_size=1000, 
#                                              window_days=45,
#                                              overlap_days=0)
#3 is too much overlap (gets stuck at 3/20 - 3/17 2020)
#2 is too much overlap gets stuck 3/13-11/2020
#1 is too much, gets stuck near end i think
