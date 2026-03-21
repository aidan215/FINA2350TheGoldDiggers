import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from arch import arch_model
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 1. Load Data
    data_path = "data/processed/gold_master_data.csv"
    if not os.path.exists(data_path):
        logger.error(f"Master data not found at {data_path}. Run previous phases first.")
        return

    df = pd.read_csv(data_path, index_col='Date', parse_dates=True)
    df = df.dropna(subset=['Log_Return', 'Monetary', 'Fiscal', 'Geopolitics'])

    # Define variables
    y = df['Log_Return']
    X = df[['Monetary', 'Fiscal', 'Geopolitics']]

    # 2. Fit Baseline GARCH(1,1)
    logger.info("Fitting Baseline GARCH(1,1) Model...")
    model_baseline = arch_model(y, mean='Constant', vol='GARCH', p=1, q=1, dist='t')
    res_baseline = model_baseline.fit(disp='off')
    
    print("\n--- BASELINE GARCH(1,1) SUMMARY ---")
    print(res_baseline.summary())

    # 3. Fit NLP-Augmented GARCH-X(1,1)
    logger.info("Fitting NLP-Augmented GARCH-X(1,1) Model...")
    model_augmented = arch_model(y, x=X, mean='ARX', vol='GARCH', p=1, q=1, dist='t')
    res_augmented = model_augmented.fit(disp='off')
    
    print("\n--- AUGMENTED GARCH-X(1,1) SUMMARY ---")
    print(res_augmented.summary())

    # 4. Extract Conditional Volatility
    vol_baseline = res_baseline.conditional_volatility
    vol_augmented = res_augmented.conditional_volatility

    # 5. Data Visualization
    logger.info("Generating volatility comparison chart...")
    plt.figure(figsize=(12, 6))
    plt.plot(vol_baseline.index, vol_baseline, label='Baseline GARCH(1,1)', color='blue', alpha=0.7)
    plt.plot(vol_augmented.index, vol_augmented, label='NLP-Augmented GARCH-X(1,1)', color='orange', alpha=0.7)
    plt.title('Conditional Volatility Comparison: Traditional vs. NLP-Augmented GARCH')
    plt.xlabel('Date')
    plt.ylabel('Volatility (%)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    os.makedirs("data/output", exist_ok=True)
    plot_path = "data/output/volatility_comparison.png"
    plt.savefig(plot_path)
    logger.info(f"Volatility comparison chart saved to {plot_path}")
    plt.close()

    # 6. Final CSV Export (RAG Export with Narratives)
    final_df = df.copy()
    final_df['Volatility_Baseline'] = vol_baseline
    final_df['Volatility_Augmented'] = vol_augmented
    
    # Re-order columns for clarity in RAG
    # Date, Close, Log_Return, Sentiment..., Vol_Baseline, Vol_Augmented, News_Context
    rag_output_path = "data/output/garch_volatility_results.csv"
    final_df.to_csv(rag_output_path)
    logger.info(f"Final RAG-compatible results exported to {rag_output_path}")

if __name__ == "__main__":
    main()
