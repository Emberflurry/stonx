#side
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

def plot_predicted_vs_actual(y_true, y_pred, title="Predicted vs Actual Returns"):
    # Reshape for sklearn LinearRegression
    y_true = np.array(y_true).reshape(-1, 1)
    y_pred = np.array(y_pred).reshape(-1, 1)

    # Fit linear regression
    reg = LinearRegression().fit(y_true, y_pred)
    y_fit = reg.predict(y_true)
    r2 = r2_score(y_pred, y_fit)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.4, label="Data", s=30)
    plt.plot(y_true, y_fit, color="red", label=f"LinReg R² = {r2:.3f}", linewidth=2)
    plt.xlabel("Actual Return")
    plt.ylabel("Predicted Return")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.axvline(0, color="gray", linestyle="--", linewidth=1)
    plt.tight_layout()
    plt.show()
# plot_predicted_vs_actual(y_train_5d, y_pred_5d, title="5D Forward Return Prediction")
