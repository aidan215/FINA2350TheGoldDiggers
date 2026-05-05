# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load data
df = pd.read_csv('fina2350_2026_dataset_for_rag.csv')
df = df[['Date', 'Volatility_Baseline', 'Volatility_Augmented']]

# Get actual values for later comparison
y = pd.read_csv('Actual_values.csv')

df_result_1 = pd.merge(df, y, on="Date", how="inner")

# Compute MSE for Baseline and Augmented models

mse_baseline_daily = mean_squared_error(df_result_1['Actual_Volatility'], df_result_1['Volatility_Baseline'])
mse_augmented_daily = mean_squared_error(df_result_1['Actual_Volatility'], df_result_1['Volatility_Augmented'])


######################## Daily volatility evaluation ########################

# Print results
print(f'MSE for Baseline Model (daily): {mse_baseline_daily}')
print(f'MSE for Augmented Model (daily): {mse_augmented_daily}')

# Computer MAE for Baseline and Augmented models - more robust to outliers

mae_baseline_daily = mean_absolute_error(df_result_1['Actual_Volatility'], df_result_1['Volatility_Baseline'])
mae_augmented_daily = mean_absolute_error(df_result_1['Actual_Volatility'], df_result_1['Volatility_Augmented'])

# Print results
print(f'MAE for Baseline Model (Daily): {mae_baseline_daily}')
print(f'MAE for Augmented Model (Daily): {mae_augmented_daily}')

#################### Weekly future realized volatility evaluation ####################

# Compute MSE for Baseline and Augmented models

mse_baseline_weekly = mean_squared_error(df_result_1['Future_Realized_Volatility_weekly'], df_result_1['Volatility_Baseline'])
mse_augmented_weekly = mean_squared_error(df_result_1['Future_Realized_Volatility_weekly'], df_result_1['Volatility_Augmented'])

# Print results
print(f'MSE for Baseline Model (Weekly): {mse_baseline_weekly}')
print(f'MSE for Augmented Model (Weekly): {mse_augmented_weekly}')

# Computer MAE for Baseline and Augmented models - more robust to outliers

mae_baseline_weekly = mean_absolute_error(df_result_1['Future_Realized_Volatility_weekly'], df_result_1['Volatility_Baseline'])
mae_augmented_weekly = mean_absolute_error(df_result_1['Future_Realized_Volatility_weekly'], df_result_1['Volatility_Augmented'])

# Print results
print(f'MAE for Baseline Model (Weekly): {mae_baseline_weekly}')
print(f'MAE for Augmented Model (Weekly): {mae_augmented_weekly}')

##################### Monthly future realized volatility evaluation ####################
# Compute MSE for Baseline and Augmented models

mse_baseline_monthly = mean_squared_error(df_result_1['Future_Realized_Volatility_monthly'], df_result_1['Volatility_Baseline'])
mse_augmented_monthly = mean_squared_error(df_result_1['Future_Realized_Volatility_monthly'], df_result_1['Volatility_Augmented'])

# Print results
print(f'MSE for Baseline Model (Monthly): {mse_baseline_monthly}')
print(f'MSE for Augmented Model (Monthly): {mse_augmented_monthly}')

# Computer MAE for Baseline and Augmented models - more robust to outliers

mae_baseline_monthly = mean_absolute_error(df_result_1['Future_Realized_Volatility_monthly'], df_result_1['Volatility_Baseline'])
mae_augmented_monthly = mean_absolute_error(df_result_1['Future_Realized_Volatility_monthly'], df_result_1['Volatility_Augmented'])

# Print results
print(f'MAE for Baseline Model (Monthly): {mae_baseline_monthly}')
print(f'MAE for Augmented Model (Monthly): {mae_augmented_monthly}')

# Plot bar chart

# Targets (3 volatility measures) and model prediction columns (2 GARCH models)
targets = {
    "Daily (Actual_Volatility)": "Actual_Volatility",
    "Weekly future vol": "Future_Realized_Volatility_weekly",
    "Monthly future vol": "Future_Realized_Volatility_monthly",
}
models_pred = {
    "GARCH Baseline": "Volatility_Baseline",
    "GARCH Augmented": "Volatility_Augmented",
}

rows = []
for target_name, y_col in targets.items():
    for model_name, pred_col in models_pred.items():
        mask = df_result_1[y_col].notna() & df_result_1[pred_col].notna()
        y_true = df_result_1.loc[mask, y_col]
        y_pred = df_result_1.loc[mask, pred_col]

        mse = mean_squared_error(y_true, y_pred)
        rows.append({
            "Volatility Measure": target_name,
            "Model": model_name,
            "n": int(mask.sum()),
            "MAE": mean_absolute_error(y_true, y_pred),
            "RMSE": float(np.sqrt(mse)),
        })

metrics = pd.DataFrame(rows)
metrics

# Plot grouped bar charts for MAE and RMSE
sns.set_style("whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)

sns.barplot(data=metrics, x="Volatility Measure", y="MAE", hue="Model", ax=axes[0])
axes[0].set_title("MAE (lower is better)")
axes[0].set_xlabel("")
axes[0].tick_params(axis="x", rotation=20)

sns.barplot(data=metrics, x="Volatility Measure", y="RMSE", hue="Model", ax=axes[1])
axes[1].set_title("RMSE (lower is better)")
axes[1].set_xlabel("")
axes[1].tick_params(axis="x", rotation=20)

for ax in axes:
    ax.legend(title="")
    ax.set_ylabel("")

plt.tight_layout()
plt.show()