#MAIN 
#full ticker sim
import pandas as pd
from single_positrader import single_positrader


def simulate_all_tickers(df, model,ticker_counts, forward_price_col='p_p5_td', 
                         return_col='r_p5_td', verbose=True,buymag=100,
                         plot=False):
    ''' sim trades by ticker, across all insider trade data undropped
    buymag not variable, val = "x WORTH of shares" to buy, NOT #
    '''
    tickers = df['ticker'].unique()
    all_results = []
    total_pnl = 0
    total_spy_pnl = 0
    total_trades = 0

    for ticker in tickers:
        try:
            results = single_positrader(
                df=df,
                ticker=ticker,
                ticker_counts = ticker_counts,
                model=model,
                forward_price_col=forward_price_col,
                return_col=return_col,buymag=buymag,
                plot=plot
            )

            if results is not None and not results.empty:
                pnl_sum = results['pnl'].sum()
                spy_sum = results['spy_pnl'].sum()
                trade_count = len(results)

                all_results.append({
                    'ticker': ticker,
                    'pnl': pnl_sum,
                    'spy_pnl': spy_sum,
                    'num_trades': trade_count
                })

                total_pnl += pnl_sum
                total_spy_pnl += spy_sum
                total_trades += trade_count

                if verbose:
                    print(f"[✓] {ticker}: {trade_count} trades | PnL: ${pnl_sum:.2f} | SPY: ${spy_sum:.2f}")

        except Exception as e:
            print(f"[✗] Error processing {ticker}: {e}")

    summary_df = pd.DataFrame(all_results).sort_values(by='pnl', ascending=False)
    print("\n=== TOTAL RESULTS ===")
    print(f"Total Trades: {total_trades} / {len(df)} possible insider trade signals across {len(summary_df)} distinct tickers")
    print(f"Total PnL off ${buymag} per trade: ${total_pnl:.2f}")
    print(f"Total SPY PnL (benchmark): ${total_spy_pnl:.2f}")
    print(f"Total Period Return: {round(100*total_pnl/(buymag*total_trades +total_pnl),2)}%")


    return summary_df
# summary_df = simulate_all_tickers(
#     df=oip_with_prices_relative,
#     ticker_counts = ticker_counts,
#     model=model_5d,
#     forward_price_col='p_p5_td',
#     return_col='r_p5_td'
# )
