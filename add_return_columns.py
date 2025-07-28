#add returns columns
def add_return_columns(df):
    price_cols = [col for col in df.columns if col.startswith('p_') and '_td' in col]
    for col in price_cols:
        return_col = col.replace('p_', 'r_')
        df[return_col] = (df[col].apply(lambda x: float(x.iloc[0]) if hasattr(x, 'iloc') else x) - df['mebuy_price']) / df['mebuy_price']
    return df
# oip_with_prices_relative = add_return_columns(oip_with_prices_relative)
# print((oip_with_prices_relative.iloc[0]))#.to_string(index=False))