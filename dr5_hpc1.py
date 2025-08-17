import re
import argparse
import numpy as np
import pandas as pd
import lightgbm as lgb

# -------------------
# CLI
# -------------------
ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--panel_out", default="mdp_trajectory_panel.csv")
ap.add_argument("--feat_out",  default="mdp_features_for_value_model.csv")
ap.add_argument("--horizon",   type=int, default=10)
ap.add_argument("--n_jobs",    type=int, default=8)
args = ap.parse_args()

INPUT_PATH = args.input
OUTPUT_PANEL_CSV = args.panel_out
OUTPUT_FEATURES_CSV = args.feat_out
H_DEFAULT = args.horizon
N_JOBS = args.n_jobs

# Your date split
TRAIN_END  = pd.Timestamp("2024-02-21")
TEST_START = pd.Timestamp("2024-02-21")
TEST_END   = pd.Timestamp("2025-07-22")

# -------------------
# Load
# -------------------
def load_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        return pd.read_csv(path)

df = load_any(INPUT_PATH).copy()

# Dates
for c in ["filing_date", "trade_date", "mebuydate"]:
    if c in df.columns:
        df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)

# -------------------
# Forward columns
# -------------------
re_price_fwd = re.compile(r"^p_p(\d+)_td$")
re_vol_fwd   = re.compile(r"^v_p(\d+)_td$")
re_ret_fwd   = re.compile(r"^ret_p_p(\d+)_td$")

fwd_price_cols = sorted([(int(re_price_fwd.match(c).group(1)), c) for c in df.columns if re_price_fwd.match(c)])
fwd_vol_cols   = sorted([(int(re_vol_fwd.match(c).group(1)), c)   for c in df.columns if re_vol_fwd.match(c)])
fwd_ret_cols   = sorted([(int(re_ret_fwd.match(c).group(1)), c)   for c in df.columns if re_ret_fwd.match(c)])

max_fwd = 0
if fwd_price_cols: max_fwd = max(max_fwd, max(k for k,_ in fwd_price_cols))
if fwd_vol_cols:   max_fwd = max(max_fwd,   max(k for k,_ in fwd_vol_cols))
if fwd_ret_cols:   max_fwd = max(max_fwd,   max(k for k,_ in fwd_ret_cols))
H = min(H_DEFAULT, max_fwd) if max_fwd > 0 else H_DEFAULT

def is_forward_col(c: str) -> bool:
    return bool(re_price_fwd.match(c) or re_vol_fwd.match(c) or re_ret_fwd.match(c))

# -------------------
# Base features (safe at entry)
# -------------------
id_like = {
    "ticker","company_name","insider_name","title","trade_type","year",
    "filing_date","trade_date","mebuydate","mebuy_price","filing_price"
}
base_feature_cols = [c for c in df.columns if (c not in id_like) and (not is_forward_col(c))]

# -------------------
# Time-varying feats (≤ t only)
# -------------------
def build_time_features(row: pd.Series, t: int) -> dict:
    feats = {}
    ret_col = f"ret_p_p{t}_td"
    price_col_t   = f"p_p{t}_td"
    price_col_tm1 = f"p_p{t-1}_td" if t-1 >= 1 else None

    ret_t = row.get(ret_col, np.nan)
    px_t  = row.get(price_col_t, np.nan)
    px_tm1 = row.get(price_col_tm1, np.nan) if price_col_tm1 else np.nan
    entry_px = row.get("mebuy_price", np.nan)

    feats["cum_ret_t"] = ret_t
    if t == 1:
        feats["ret_1d"] = (px_t / entry_px - 1.0) if pd.notna(px_t) and pd.notna(entry_px) and entry_px != 0 else (ret_t if pd.notna(ret_t) else np.nan)
    else:
        feats["ret_1d"] = (px_t / px_tm1 - 1.0) if pd.notna(px_t) and pd.notna(px_tm1) and px_tm1 != 0 else np.nan
    return feats

# -------------------
# Build panel
# -------------------
rows = []
df_reset = df.reset_index(drop=True)
for idx, row in df_reset.iterrows():
    trade_id = idx
    entry_dt = row.get("mebuydate", pd.NaT)
    entry_px = row.get("mebuy_price", np.nan)
    ticker   = row.get("ticker", None)

    for t in range(1, H+1):
        price_t = row.get(f"p_p{t}_td", np.nan)
        ret_t   = row.get(f"ret_p_p{t}_td", np.nan)
        if pd.isna(price_t) and pd.isna(ret_t):
            continue

        base_feats = row[base_feature_cols].to_dict()
        tv_feats   = build_time_features(row, t)
        days_left  = H - t

        payoff_t = ret_t
        if pd.isna(payoff_t) and pd.notna(price_t) and pd.notna(entry_px) and entry_px != 0:
            payoff_t = price_t / entry_px - 1.0

        rows.append({
            "trade_id": trade_id,
            "ticker": ticker,
            "entry_date": entry_dt,
            "t": t,
            "days_left": days_left,
            "payoff_t": payoff_t,
            "SELL_value": payoff_t,
            **base_feats,
            **tv_feats
        })

panel = pd.DataFrame(rows)

# Split by entry date
def label_set(d: pd.Timestamp) -> str:
    if pd.isna(d): return "drop"
    if d <= TRAIN_END: return "train"
    if (d >= TEST_START) and (d <= TEST_END): return "test"
    return "drop"

panel["set"] = panel["entry_date"].apply(label_set)
panel = panel[panel["set"] != "drop"].copy()

# -------------------
# Backward induction (LightGBM; NaN-native; numeric-only features for stability)
# -------------------
panel_bi = panel.copy()
panel_bi["V_target"] = np.nan

exclude_feats = {"trade_id","ticker","entry_date","set","V_target","payoff_t","SELL_value"}
numeric_cols = panel_bi.select_dtypes(include=[np.number]).columns.tolist()
numeric_features = [c for c in numeric_cols if c not in exclude_feats]

# Ensure time coords present
if "t" not in numeric_features: numeric_features = ["t"] + numeric_features
if "days_left" not in numeric_features:
    numeric_features = ["days_left"] + [c for c in numeric_features if c != "days_left"]

# Horizon boundary
panel_bi.loc[panel_bi["t"] == H, "V_target"] = panel_bi.loc[panel_bi["t"] == H, "payoff_t"]

def fit_lgbm(X, y):
    model = lgb.LGBMRegressor(
        n_estimators=1200, learning_rate=0.03, num_leaves=127,
        subsample=0.8, colsample_bytree=0.8, min_child_samples=40,
        n_jobs=N_JOBS, random_state=42
    )
    model.fit(X, y)
    return model

for k in range(H-1, 0, -1):
    train_mask = panel_bi["t"] >= (k+1)
    X_train = panel_bi.loc[train_mask, numeric_features]
    y_train = panel_bi.loc[train_mask, "V_target"]
    good = ~y_train.isna()
    X_train = X_train.loc[good]
    y_train = y_train.loc[good]

    if len(X_train) < 50:
        hold_pred = panel_bi.loc[panel_bi["t"] == k, "payoff_t"].values
    else:
        m = fit_lgbm(X_train, y_train.values)
        X_k = panel_bi.loc[panel_bi["t"] == k, numeric_features]
        hold_pred = m.predict(X_k)

    sell_val = panel_bi.loc[panel_bi["t"] == k, "SELL_value"].values
    v_k = np.maximum(sell_val, hold_pred)
    panel_bi.loc[panel_bi["t"] == k, "V_target"] = v_k

# -------------------
# Save outputs
# -------------------
panel_bi.to_csv(OUTPUT_PANEL_CSV, index=False)

meta_cols = ["trade_id","ticker","entry_date","t","days_left","set","SELL_value","V_target"]
keep_cols = meta_cols + [c for c in numeric_features if c not in {"t","days_left"}]
# uniqueness/preserve order
seen, ordered_keep = set(), []
for c in keep_cols:
    if c in panel_bi.columns and c not in seen:
        ordered_keep.append(c); seen.add(c)

feat_df = panel_bi[ordered_keep].copy()
feat_df.to_csv(OUTPUT_FEATURES_CSV, index=False)

print(f"Done. H={H}")
print(f"Rows panel: {len(panel_bi):,}")
print(f"Rows train: {(panel_bi['set']=='train').sum():,}")
print(f"Rows test : {(panel_bi['set']=='test').sum():,}")
print(f"Wrote: {OUTPUT_PANEL_CSV}")
print(f"Wrote: {OUTPUT_FEATURES_CSV}")
