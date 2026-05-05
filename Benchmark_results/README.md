# Benchmark_results

This folder contains the benchmark/evaluation pipeline used to compare LLM-predicted volatility buckets against ground-truth volatility measures (daily, weekly future realized, monthly future realized), plus a baseline GARCH comparison.

## Directory layout

- `data_cleaning.py` — loads model outputs (LLM + RAG), does light column cleanup, and writes a single combined `results.pkl`.
- `results_daily.py` — evaluates predictions against **daily** `Actual_Volatility`.
- `results_weekly.py` — evaluates predictions against **weekly** `Future_Realized_Volatility_weekly`.
- `results_monthly.py` — evaluates predictions against **monthly** `Future_Realized_Volatility_monthly`.
- `garch_analysis.py` — compares GARCH baseline/augmented volatility predictions to the same ground truths.

Data/artifacts used by the scripts:

- `Actual_values.csv` — ground-truth file with `Date`, `Actual_Volatility`, `Future_Realized_Volatility_weekly`, `Future_Realized_Volatility_monthly`.
- `llm_result/` — per-model CSVs: `claude.csv`, `deepseek.csv`, `gemini.csv`, `gpt.csv`, `qwen.csv`, `ollama8b.csv`.
- `rag_result/` — RAG outputs used by `data_cleaning.py`:
  - `rag.csv`
  - `dates_2026.csv`
- `results/` — text outputs written by the evaluation scripts.

## Prerequisites

From this directory, create/activate a Python environment that has:

- `pandas`, `numpy`
- `scikit-learn`
- `matplotlib`
- `seaborn` (used by `garch_analysis.py`)

Example install:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

## How to run (recommended order)

Run commands from inside `Benchmark_results/`:

```bash
cd Benchmark_results
```

### 1) Build the combined results object

```bash
python data_cleaning.py
```

Outputs:

- `results.pkl` — a Python pickle containing a dictionary of DataFrames keyed by model name (and `rag`).

### 2) Evaluate LLM bucket predictions vs ground truth

Daily evaluation:

```bash
python results_daily.py
```

Weekly evaluation:

```bash
python results_weekly.py
```

Monthly evaluation:

```bash
python results_monthly.py
```

Each script:

- Loads `Actual_values.csv` and `results.pkl`
- Buckets the target volatility into 5 quintiles using `pd.qcut` (creates `bucket` and `bucket_log`; evaluation uses `bucket`)
- Computes regression metrics for `Volatility_Market_Adjusted` vs the target: MSE and MAE
- Converts the model’s textual bucket labels (`Very Low` … `Very High`) to integers 0–4
- Computes quadratic-weighted Cohen’s kappa between the model bucket and the ground-truth quintile bucket
- Writes a classification report to a text file under `results/`

Text outputs:

- `results/classification_output_daily.txt`
- `results/classification_output_weekly.txt`
- `results/classification_output_monthly.txt`

Plots (saved in the current directory):

- `model_performance.png` (bar chart for MSE/MAE)
- `model_kappa.png`
- `model_accuracy.png`

Important: the plot filenames are the same in all three scripts, so running weekly/monthly after daily will overwrite these PNGs. If you want to keep each set, rename or move them between runs.

### 3) GARCH baseline vs augmented comparison

```bash
python garch_analysis.py
```

What it does:

- Loads `fina2350_2026_dataset_for_rag.csv` and keeps `Date`, `Volatility_Baseline`, `Volatility_Augmented`
- Merges with `Actual_values.csv` on `Date`
- Prints MAE/MSE for baseline vs augmented against daily/weekly/monthly targets
- Builds a small metrics table with `MAE` and `RMSE` and visualizes it

Note: `garch_analysis.py` currently calls `plt.show()`, so you may need a GUI backend (or run it in a notebook) to see the plot window.

## Common issues

- **Missing packages (e.g., `ModuleNotFoundError: pandas`)**: install the prerequisites in the Python environment you’re using to run the scripts.
- **File not found**: run from `Benchmark_results/` so relative paths like `./rag_result/rag.csv` resolve correctly.
- **Bucket conversion produces NaNs**: the mapping step expects `Volatility_Market_Adjusted_Bucket` values to be exactly one of `Very Low`, `Low`, `Medium`, `High`, `Very High`.
