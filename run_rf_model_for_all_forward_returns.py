#MAIN
# NEED MODELSDICT
#forward window choosing testing
from sklearn.metrics import precision_score, recall_score, f1_score,r2_score
import numpy as np
from train_rf_forward_return_model import train_rf_forward_return_model
import pandas as pd


def run_rf_model_for_all_forward_returns(df, forward_return_cols,plot=False):
    '''
    df = oip_with_prices_relative or similar DataFrame with forward return columns
    forward_return_cols = list of columns to use as forward returns, e.g. ['r_p1_td'...
    randomforest + BINARY DIRECTION PREDICTION (summary has both)
    '''
    modelsmetrics = dict()
    models_dict = dict()
    for col in forward_return_cols:
        print(f"\n--- Training model for: {col} ---")

        # Train model
        model, X_train, y_train, y_pred = train_rf_forward_return_model(df, forward_return_col=col)
        models_dict[col] = model

        # Evaluation metrics
        # R² and RMSE
        r2 = r2_score(y_train, y_pred)
        rmse = np.sqrt(np.mean((y_train - y_pred) ** 2))
        print(f"R²: {r2:.4f}")
        print(f"RMSE: {rmse:.4f}")

        #conv to binary for precision/recall - model pred of dir of returns?
        # Convert to binary direction (1 if return > 0, else 0)
        y_true_binary = (y_train > 0).astype(int)
        y_pred_binary = (y_pred > 0).astype(int)
        precision = precision_score(y_true_binary, y_pred_binary)
        recall = recall_score(y_true_binary, y_pred_binary)
        f1 = f1_score(y_true_binary, y_pred_binary)
        print(f"Precision (Direction): {precision:.4f}")
        print(f"Recall (Direction): {recall:.4f}")
        print(f"F1 Score (Direction): {f1:.4f}")

        # Feature importances
        feature_importance = pd.Series(model.feature_importances_, index=X_train.columns)
        modelsmetrics[col] = [r2,rmse,precision,recall,f1]
        # Plot
        if plot:
          import plot_predicted_vs_actual
          plot_predicted_vs_actual(y_train, y_pred, title=f"{col}: Predicted vs Actual")
    return modelsmetrics,models_dict
# forward_cols = [col for col in oip_with_prices_relative.columns if col.startswith("r_p")]
# modelsmetrics,models_dict = run_rf_model_for_all_forward_returns(oip_with_prices_relative, forward_cols)
