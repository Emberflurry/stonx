#clean out failed/delisted tickers
def remove_failed_tickers(oip_df, failedtickers):
    """
    Remove rows from oip_df where the ticker is in the failedtickers list.
    
    Parameters:
        oip_df (pd.DataFrame): Original dataframe with insider trade data.
        failedtickers (list): List of tickers to exclude (e.g., delisted or no price data).
        
    Returns:
        pd.DataFrame: Cleaned dataframe with failed tickers removed.
    """
    cleaned_df = oip_df[~oip_df['ticker'].isin(failedtickers)].copy()
    print(f"Removed {len(oip_df) - len(cleaned_df)} rows with failed tickers.")
    return cleaned_df
# oip_clean = remove_failed_tickers(oip_with_prices, failedtickersunique)