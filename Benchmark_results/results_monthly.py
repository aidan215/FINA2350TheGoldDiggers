# Import libraries

import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import cohen_kappa_score
from contextlib import redirect_stdout
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# import data
y = pd.read_csv('Actual_values.csv')

with open("results.pkl", "rb") as f:
    results = pickle.load(f)

models = results.keys()

# Monthly future realized volatility evaluation
vol_col = "Future_Realized_Volatility_monthly"
vol = pd.to_numeric(y[vol_col], errors="coerce")

# Nonparametric (distribution-free) quintiles: ~20% of observations per bucket
y["bucket"] = pd.qcut(vol, q=5, labels=False, duplicates="drop")

# Volatility is typically right-skewed; log-vol quintiles are often more stable/meaningful
eps = 1e-12
y["bucket_log"] = pd.qcut(np.log(vol.clip(lower=eps)), q=5, labels=False, duplicates="drop")

# Quick sanity check: proportions in each bucket (should be ~0.2 each, unless ties/NaNs)
print(pd.DataFrame({
    "bucket": y["bucket"].value_counts(normalize=True, dropna=False).sort_index(),
    "bucket_log": y["bucket_log"].value_counts(normalize=True, dropna=False).sort_index(),
}))

# merge results with y on 'Date' for every model
for model in models:
    results[model] = results[model].merge(y[["Date", "Future_Realized_Volatility_monthly", "bucket"]], on="Date", how="left")
    
    # calculate mse between predicted volatility and actual volatility for each bucket using sklearn's mean_squared_error function, and store in a new column in results[model] called 'mse'
    results[model]["mse"] = mean_squared_error(results[model]["Volatility_Market_Adjusted"], results[model]['Future_Realized_Volatility_monthly'])
    
    results[model]["mae"] = mean_absolute_error(results[model]["Volatility_Market_Adjusted"], results[model]['Future_Realized_Volatility_monthly'])

# for each model convert very low, low, medium, high, very high to 0, 1, 2, 3, 4 respectively
for model in models:
    results[model]["Volatility_Market_Adjusted_Bucket"] = results[model]["Volatility_Market_Adjusted_Bucket"].map({
        "Very Low": 0,
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Very High": 4
    })

# print mse and mae for each model
for model in models:
    print(f"{model}: mse = {results[model]['mse'].iloc[0]}, mae = {results[model]['mae'].iloc[0]}")

# Measure kappa score which is a measure of agreement between two raters (in this case, the model's bucket and the actual bucket), taking into account the possibility of agreement occurring by chance. Use the cohen_kappa_score function from sklearn.metrics, with weights="quadratic" to give more weight to larger disagreements (e.g. predicting "Very Low" when it's actually "Very High" is worse than predicting "Low" when it's actually "High"). Print the kappa score for each model.
for model in models:
    print(f"Model: {model}")
    
    a = results[model]["bucket"]
    b = results[model]["Volatility_Market_Adjusted_Bucket"]

    mask = a.notna() & b.notna()
    a2, b2 = a[mask], b[mask]
    
    print("kappa (quadratic):", cohen_kappa_score(a2, b2, weights="quadratic"))

out_path = "results/classification_output_monthly.txt"

with open(out_path, "w") as f, redirect_stdout(f):
    for model in models:
        print(f"===== Model: {model} =====")

        a = results[model]["bucket"]
        b = results[model]["Volatility_Market_Adjusted_Bucket"]

        mask = a.notna() & b.notna()
        a2, b2 = a[mask], b[mask]

        print("n:", int(mask.sum()))
        print("accuracy:", accuracy_score(a2, b2))
        print("confusion_matrix:\n", confusion_matrix(a2, b2))
        print("classification_report:\n", classification_report(a2, b2, digits=3, zero_division=0))
        print()

print(f"Saved to {out_path}")

# print all model accuracy scores in a table
accuracy_scores = []
for model in models:
    a = results[model]["bucket"]
    b = results[model]["Volatility_Market_Adjusted_Bucket"]

    mask = a.notna() & b.notna()
    a2, b2 = a[mask], b[mask]

    accuracy_scores.append({
        "model": model,
        "accuracy": accuracy_score(a2, b2)
    })
accuracy_df = pd.DataFrame(accuracy_scores)
print(accuracy_df)

# plot mse and mae for each model in a bar chart using matplotlib, with models on the x-axis and mse/mae on the y-axis, and save the plot as 'model_performance.png'

mse_values = [results[model]["mse"].iloc[0] for model in models]
mae_values = [results[model]["mae"].iloc[0] for model in models]
x = range(len(models))
plt.bar(x, mse_values, width=0.4, label='MSE', align='center')
plt.bar(x, mae_values, width=0.4, label='MAE', align='edge')
plt.xticks(x, models)
plt.ylabel('Error')
plt.title('Model Performance')
plt.legend()
plt.tight_layout()
plt.savefig('model_performance.png')
print("Saved model performance plot as 'model_performance.png'")

# plot the kappa scores for each model in a bar chart using matplotlib, with models on the x-axis and kappa score on the y-axis, and save the plot as 'model_kappa.png'
kappa_values = []
for model in models:
    a = results[model]["bucket"]
    b = results[model]["Volatility_Market_Adjusted_Bucket"]

    mask = a.notna() & b.notna()
    a2, b2 = a[mask], b[mask]

    kappa = cohen_kappa_score(a2, b2, weights="quadratic")
    kappa_values.append(kappa)
x = range(len(models))
plt.bar(x, kappa_values, width=0.4, label='Kappa Score', align='center')
plt.xticks(x, models)
plt.ylabel('Kappa Score')
plt.title('Model Kappa Scores')
plt.legend()
plt.tight_layout()
plt.savefig('model_kappa.png')
print("Saved model kappa plot as 'model_kappa.png'")

# plot the accuracy score and have the formula for accuracy score in the title of the plot, and save the plot as 'model_accuracy.png'
accuracy_values = []
for model in models:
    a = results[model]["bucket"]
    b = results[model]["Volatility_Market_Adjusted_Bucket"]

    mask = a.notna() & b.notna()
    a2, b2 = a[mask], b[mask]

    accuracy = accuracy_score(a2, b2)
    accuracy_values.append(accuracy)
x = range(len(models))
plt.bar(x, accuracy_values, width=0.4, label='Accuracy', align='center')
plt.xticks(x, models)
plt.ylabel('Accuracy')
plt.title('Model Accuracy (Accuracy = (TP + TN) / Total)')
plt.legend()
plt.tight_layout()
plt.savefig('model_accuracy.png')
print("Saved model accuracy plot as 'model_accuracy.png'")