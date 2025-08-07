from oi_bulk_get_fns import get_all_openinsider_chunks,openinsider_url
import pandas as pd
filename = 'oi_rawpull_ymd_2019_01_01_2025_08_06_incl.csv'
oipmega1 = pd.read_csv(filename, usecols=lambda col: col != pd.read_csv(filename, nrows=0).columns[0])
#YF PRICE/vol DATA ATTEMPT 1
from add_relative_prices2 import add_prices_to_oip_precise
window = [1,2,3,4,5,6,7,8,9,10,15,20,35,60,90,130,180,245]
oip_w_prices, error_dict = add_prices_to_oip_precise(oipmega1, fwindow=window, bwindow=window)
oip_w_prices.to_csv('oipmega_post_yf1.csv',index=False)