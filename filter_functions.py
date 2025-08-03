import pandas as pd

def get_window_columns(df, prefix):
    """Return a sorted list of all columns starting with a given prefix."""
    return sorted([col for col in df.columns if col.startswith(prefix)])

def add_addv_columns(df, price_prefix='p_m', vol_prefix='v_m'):
    price_cols = get_window_columns(df, price_prefix)
    vol_cols = get_window_columns(df, vol_prefix)
    addv_cols = []
    for pcol, vcol in zip(price_cols, vol_cols):
        addv_col = 'addv' + pcol[1:]   # e.g. addv_m5_td
        df[addv_col] = df[pcol] * df[vcol]
        addv_cols.append(addv_col)
    return df, addv_cols

def flag_first_failure(
    df, 
    addv_cols, 
    vol_cols, 
    price_cols, 
    min_addv=5_000_000, 
    min_volume=100, 
    min_price=1.0
):
    flags = []
    for _, row in df.iterrows():
        # 1. Zero volume
        if any((row[v] == 0 or pd.isnull(row[v])) for v in vol_cols):
            flags.append('zero_volume')
            continue
        # 2. Zero price
        if any(pd.isnull(row[p]) for p in price_cols):
            flags.append('zero_price')
            continue
        # 3. Low volume
        if any(row[v] < min_volume for v in vol_cols):
            flags.append('low_vol')
            continue
        # 4. Low price
        if any(row[p] < min_price for p in price_cols):
            flags.append('low_price')
            continue
        # 5. Low addv
        if any(row[a] < min_addv or pd.isnull(row[a]) for a in addv_cols):
            flags.append('low_addv')
            continue
        # Passes all checks
        flags.append('pass')
    df = df.copy()
    df['liquidity_flag'] = flags
    return df

def liquidity_filter_first_failure(
    df, 
    addv_cols, 
    vol_cols, 
    price_cols, 
    min_addv=5_000_000, 
    min_volume=100, 
    min_price=1.0,
    verbose=True
):
    df_flagged = flag_first_failure(df, addv_cols, vol_cols, price_cols, min_addv, min_volume, min_price)
    filtered = df_flagged[df_flagged['liquidity_flag'] == 'pass'].copy()
    dropped = df_flagged[df_flagged['liquidity_flag'] != 'pass']
    if verbose:
        reason_counts = dropped['liquidity_flag'].value_counts()
        total = len(df_flagged)
        print("\n--- Liquidity filter exclusion summary (first failure wins[0vol/0p/lovol/lop/loaddv]) ---")
        for reason, count in reason_counts.items():
            print(f"{reason:12}: {count} rows ({count/total:.1%})")
        print(f"\nKept {len(filtered)} / {total} rows ({len(filtered)/total:.1%}) after filtering.")
    return filtered, dropped, df_flagged

# === Example usage ===
# price_cols = [f'p_m{n}_td' for n in fwindow]
# vol_cols   = [f'v_m{n}_td' for n in fwindow]
# oip_w_prices, addv_cols = add_addv_columns(oip_w_prices, price_prefix='p_m', vol_prefix='v_m')
# oip_liquid, oip_excluded, oip_flagged = liquidity_filter_first_failure(
#     oip_w_prices, addv_cols, vol_cols, price_cols,
#     min_addv=5_000_000, min_volume=100, min_price=1.0
# )
