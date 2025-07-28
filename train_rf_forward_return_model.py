# training function for a given forward return window
#forward window returns - param choice

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np

def train_rf_forward_return_model(df, forward_return_col='r_p5_td', random_state=42):
    # Select predictor columns
    return_cols = [col for col in df.columns if col.startswith('r_m')]  # past returns
    other_features = ['qty', 'owned', 'value', 'd_own_plus%']
    features = return_cols + other_features

    # Prepare X and y
    X = df[features].copy()
    y = df[forward_return_col].copy()

    # Drop rows with missing values in X or y
    data = pd.concat([X, y], axis=1).dropna()
    X_clean = data[features]
    y_clean = data[forward_return_col]

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=random_state)
    model.fit(X_clean, y_clean)

    # Predict on training data
    y_pred = model.predict(X_clean)

    # Evaluation metrics
    r2 = r2_score(y_clean, y_pred)
    rmse = np.sqrt(mean_squared_error(y_clean, y_pred))


    print(f"📈 R²: {r2:.4f}")
    print(f"📉 RMSE: {rmse:.4f}")
    print(f"🔢 Samples used: {len(y_clean)}\n")

    # Feature importances
    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print("🌲 Feature Importances:")
    print(importances)

    return model, X_clean, y_clean, y_pred
# model_5d, X_train_5d, y_train_5d, y_pred_5d = train_rf_forward_return_model(oip_with_prices_relative, forward_return_col='r_p5_td')
