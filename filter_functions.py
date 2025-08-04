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
    min_price=1.0,
    last_n=5  # <--- only consider last n windows
):
    flags = []
    # Only check the *last* n columns in each list (lookback windows)
    last_vol_cols = vol_cols[-last_n:]
    last_price_cols = price_cols[-last_n:]
    last_addv_cols = addv_cols[-last_n:]

    for _, row in df.iterrows():
        # 1. Zero volume
        if any((row[v] == 0 or pd.isnull(row[v])) for v in last_vol_cols):
            flags.append('zero_volume')
            continue
        # 2. Zero price
        if any(pd.isnull(row[p]) for p in last_price_cols):
            flags.append('zero_price')
            continue
        # 3. Low volume
        if any(row[v] < min_volume for v in last_vol_cols):
            flags.append('low_vol')
            continue
        # 4. Low price
        if any(row[p] < min_price for p in last_price_cols):
            flags.append('low_price')
            continue
        # 5. Low addv
        if any(row[a] < min_addv or pd.isnull(row[a]) for a in last_addv_cols):
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
    last_n=5,
    verbose=True
):
    df_flagged = flag_first_failure(
        df, addv_cols, vol_cols, price_cols, min_addv, min_volume, min_price, last_n=last_n)
    filtered = df_flagged[df_flagged['liquidity_flag'] == 'pass'].copy()
    dropped = df_flagged[df_flagged['liquidity_flag'] != 'pass']
    if verbose:
        reason_counts = dropped['liquidity_flag'].value_counts()
        total = len(df_flagged)
        print("\n--- Liquidity filter exclusion summary (first failure wins[0vol/0p/lovol/lop/loaddv], last_n = {}) ---".format(last_n))
        for reason, count in reason_counts.items():
            print(f"{reason:12}: {count} rows ({count/total:.1%})")
        print(f"\nKept {len(filtered)} / {total} rows ({len(filtered)/total:.1%}) after filtering.")
    return filtered, dropped, df_flagged
