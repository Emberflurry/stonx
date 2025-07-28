#MAIN
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import yfinance as yf
import pandas as pd
import numpy as np

def single_positrader(df, ticker, model,ticker_counts, forward_price_col='p_p5_td', return_col='r_p5_td',
                      buymag=1000, plot=True):
    '''
    only buys if predicted return > 0
    model pick from models_dict[*whatever u pick forward_price_col to be*]
    buymag is how much $ worth of shares (and comparable $SPY) to buy
    fwdpricecol = ie: p_p5_td for 5d forecast
    retcol = ie: r_p5_td for 5d forecast
    '''
    df_ticker = df[df['ticker'] == ticker].copy()

    transactions = []
    spy_returns = []
    spy_pnls = []
    for idx, row in df_ticker.iterrows():
        try:
            # Prepare features
            feature_cols = [col for col in df.columns if col.startswith('r_m') or col in ['qty', 'owned', 'value', 'd_own_plus%']]
            X_row_df = pd.DataFrame([row[feature_cols].values], columns=feature_cols)
            X_row_df = X_row_df[model.feature_names_in_]  # Force correct order
            predicted_return = model.predict(X_row_df)[0]

            mebuy_price = row['mebuy_price']
            actual_sell_price = row[forward_price_col]
            mebuy_date = pd.to_datetime(row['mebuydate'])

            if pd.notna(mebuy_price) and pd.notna(actual_sell_price) and predicted_return > 0:
                shares_bought = buymag / mebuy_price
                predicted_sell_price = mebuy_price * (1 + predicted_return)
                sell_value = shares_bought * actual_sell_price
                pnl = sell_value - buymag
                
                transactions.append({
                    'ticker': ticker,
                    'mebuy_date': mebuy_date,
                    'predicted_return': predicted_return,
                    'mebuy_price': mebuy_price,
                    'predicted_sell_price': predicted_sell_price,
                    'actual_sell_price': actual_sell_price,
                    'shares_bought': shares_bought,
                    'sell_value': sell_value,
                    'pnl': pnl
                })

                match = re.search(r'p_([mp])(\d+)_td', forward_price_col)
                if match:
                    direction = match.group(1)  # 'p' or 'm'
                    days = int(match.group(2))  # '5', '10', etc.
                    if direction == 'm':
                        trading_days = -days
                    else:
                        trading_days = days
                    sell_day = mebuy_date + pd.tseries.offsets.BDay(trading_days)
                    # Fetch S&P 500 (SPY) prices between mebuy_date and sell_day
                    try:
                        spy_hist = yf.download('SPY', start=mebuy_date - pd.Timedelta(days=3), end=sell_day + pd.Timedelta(days=3), progress=False,auto_adjust=True)['Close']
                        spy_buy_date = spy_hist.index.asof(mebuy_date)
                        spy_sell_date = spy_hist.index.asof(sell_day)

                        spy_buy_price = float(spy_hist.loc[spy_buy_date].iloc[0])
                        spy_sell_price = float(spy_hist.loc[spy_sell_date].iloc[0])

                        spy_return = (spy_sell_price - spy_buy_price) / spy_buy_price
                        spy_pnl = buymag * spy_return
                        spy_returns.append(spy_return)
                        spy_pnls.append(spy_pnl)
                        print(f"[SP500] From {mebuy_date.date()} to {sell_day.date()}: SPY ${spy_buy_price:.2f} → ${spy_sell_price:.2f} | Return: {spy_return:.4f} | PnL: ${spy_pnl:.2f}")
                    except Exception as e:
                        print(f"Failed to get SPY return for row {idx}: {e}")
                        spy_return = np.nan
                        spy_pnl = np.nan
                        spy_returns.append(np.nan)
                        spy_pnls.append(np.nan)


                else:
                    print(f"Invalid forward_price_col format: {forward_price_col} — skipping")
                    continue

                

                if plot:
                  plt.figure(figsize=(6, 4))
                  plt.plot([mebuy_date, sell_day], [mebuy_price, predicted_sell_price], 'r--', label="Predicted Trajectory")
                  plt.plot([mebuy_date, sell_day], [mebuy_price, actual_sell_price], 'g--', label="Actual Trajectory")

                  plt.scatter(mebuy_date, mebuy_price, color='red', label='Buy Price')
                  plt.scatter(sell_day, predicted_sell_price, color='purple', label='Predicted Sell Price')
                  plt.scatter(sell_day, actual_sell_price, color='green', label='Actual Sell Price')

                  plt.title(f'{ticker} Trade on {mebuy_date.date()}')
                  plt.xlabel('Date')
                  plt.ylabel('Price')
                  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                  plt.gcf().autofmt_xdate()
                  plt.legend()
                  plt.grid(True)
                  plt.tight_layout()
                  plt.show()

        except Exception as e:
            print(f"Error at row {idx}: {e}")
            continue

    results_df = pd.DataFrame(transactions)
    results_df['spy_return'] = spy_returns
    results_df['spy_pnl'] = spy_pnls
    if 'pnl' in results_df.columns and not results_df.empty:
        total_trades = len(results_df)
        total_pnl = results_df['pnl'].sum()
        avg_return = results_df['pnl'].mean()
    else:
        total_trades = 0
        total_pnl = 0
        avg_return = 0

    # Get the total number of insider trades available for this ticker (denominator)
    total_possible_trades = ticker_counts.get(ticker, 0)

    print(f"\n[ Simulation for {ticker} ]")
    print(f"Total Trades Taken (only attempts posi(+) predictions): {total_trades} / {total_possible_trades} Total Insider Trades Available")
    #print(f": ")
    print(f"Total PnL from ${buymag} worth of shares/trade: ${total_pnl:.2f}")
    print(f'Total Cash Invested: ${buymag*total_trades}')
    print(f"Average Return per Trade: ${avg_return:.2f}")
    if buymag >0 and total_trades*buymag +total_pnl > 0:
      print(f'Total Period Return: {round(100*total_pnl/(buymag*total_trades +total_pnl),2)}%')
    print(f'Total $SPY PnL from ${buymag} buy/sell@same dates: ${round(sum(spy_pnls),2)}')

    return results_df
# results = single_positrader(
#     df=oip_with_prices_relative,
#     ticker='FYBR',
#     ticker_counts = ticker_counts,
#     model=models_dict['r_p5_td'],
#     forward_price_col='p_p5_td',
#     return_col='r_p5_td',
#     buymag=100,
#     plot=False
# )
# print(results)