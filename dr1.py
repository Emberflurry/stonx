#5/01/22 - 23
from get_oip_1p import get_oip_1p
from add_prices_to_oip import add_prices_to_oip
from remove_failed_tickers import remove_failed_tickers
from add_relative_prices import add_relative_prices
from add_return_columns import add_return_columns
from train_rf_forward_return_model import train_rf_forward_return_model
from plot_predicted_vs_actual import plot_predicted_vs_actual



oiurl = 'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr=05%2F01%2F2022+-+05%2F01%2F2023&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1'
oip = get_oip_1p(oiurl)

print(oip.head())
print('number of rows:', len(oip))
tickers = oip["ticker"].unique().tolist()


oip_with_prices,failedtickers = add_prices_to_oip(oip)
failedtickersunique = list(set(failedtickers))


oip_clean = remove_failed_tickers(oip_with_prices, failedtickersunique)


oip_with_prices_relative = add_relative_prices(oip_clean)
print(oip_with_prices_relative.head(1))
print(oip_with_prices_relative.columns)


oip_with_prices_relative = add_return_columns(oip_with_prices_relative)
print((oip_with_prices_relative.iloc[0]))#.to_string(index=False))


model_5d, X_train_5d, y_train_5d, y_pred_5d = train_rf_forward_return_model(oip_with_prices_relative, forward_return_col='r_p5_td')

#NOTE OPT: 5dfwd pred vs actual:
#plot_predicted_vs_actual(y_train_5d, y_pred_5d, title="5D Forward Return Prediction")

