
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from statsmodels.stats.diagnostic import acorr_ljungbox
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Paths
    master_path = "data/output/fina2350_master_dataset_for_rag.csv"
    sentiment_path = "data/processed/autonomous_news_sentiment.csv"
    
    if not os.path.exists(master_path):
        logger.error(f"Master file not found at {master_path}")
        return

    df = pd.read_csv(master_path, index_col='Date', parse_dates=True)
    df_sent = pd.read_csv(sentiment_path, parse_dates=['Date'])
    
    print("====================================================")
    print("   FINA2350 DATASET VALIDATION REPORT")
    print("====================================================\n")

    # 1. Temporal & Missing Data Checks
    all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    trading_dates = df.index.unique()
    missing_trading_days = len(all_dates) - len(trading_dates)
    
    print(f"--- 1. Temporal & Missing Data ---")
    print(f"Date Range: {df.index.min().date()} to {df.index.max().date()}")
    print(f"Total Observations: {len(df)}")
    print(f"Calendar Days in Range: {len(all_dates)}")
    print(f"Dropped Days (Weekends/Holidays/Missing): {missing_trading_days} ({missing_trading_days/len(all_dates):.1%})")
    
    # Check if we are losing news on weekends
    sent_dates = df_sent['Date'].dt.date.unique()
    master_dates = df.index.date
    news_lost = [d for d in sent_dates if d not in master_dates]
    print(f"Dates with sentiment data lost due to Inner Join (Closed Markets): {len(news_lost)}")
    print("\n")

    # 2. Sentiment Scoring Consistency
    print(f"--- 2. Sentiment Scoring Consistency ---")
    sentiment_cols = ['Monetary', 'Fiscal', 'Geopolitics']
    stats_df = df[sentiment_cols].describe().loc[['min', 'max', 'mean', 'std']]
    print(stats_df)
    
    corr_matrix = df[sentiment_cols].corr()
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    high_corr = corr_matrix.unstack().sort_values(ascending=False)
    high_corr = high_corr[high_corr < 1].head(1)
    if not high_corr.empty and high_corr.iloc[0] > 0.8:
        print(f"WARNING: High collinearity detected between {high_corr.index[0]}: {high_corr.iloc[0]:.2f}")
    print("\n")

    # 3. Log Return Distribution & Stationarity
    print(f"--- 3. Log Return Distribution ---")
    y = df['Log_Return'].dropna()
    
    # ADF Test for Stationarity
    adf_res = adfuller(y)
    print(f"ADF Statistic: {adf_res[0]:.4f}")
    print(f"p-value: {adf_res[1]:.4e}")
    if adf_res[1] < 0.05:
        print("Result: Stationarity confirmed (p < 0.05)")
    else:
        print("WARNING: Series may not be stationary.")
        
    # Outlier Detection
    z_scores = np.abs(stats.zscore(y))
    outliers = (z_scores > 3).sum()
    print(f"Extreme Outliers (>3 Std Dev): {outliers} ({outliers/len(y):.1%})")
    print("\n")

    # 4. Text Cleaning & Context Integrity
    print(f"--- 4. Text Cleaning & Context Integrity ---")
    # Handle NaNs by converting to string first
    df['Context_Length'] = df['News_Context'].fillna('').astype(str).apply(len)
    short_context = df[df['Context_Length'] < 100]
    print(f"Average Context Length (Characters): {df['Context_Length'].mean():.0f}")
    print(f"Rows with very short context (<100 chars): {len(short_context)} ({len(short_context)/len(df):.1%})")
    if not short_context.empty:
        print("Sample short context dates:", short_context.index[:3].date)
    print("\n")

    # 5. Residual Diagnostics (Baseline GARCH)
    print(f"--- 5. Baseline GARCH Residual Checks ---")
    # We use the results from the master file if available or we estimate quickly
    # Note: This checks if the Baseline model is 'clean'
    vol_resid = df['Log_Return'] / df['Volatility_Baseline']
    
    # Ljung-Box for autocorrelation in squared residuals
    lb_test = acorr_ljungbox(vol_resid**2, lags=[10], return_df=True)
    lb_p = lb_test['lb_pvalue'].values[0]
    print(f"Ljung-Box p-value (Squared Residuals, lag 10): {lb_p:.4f}")
    if lb_p > 0.05:
        print("Result: No significant conditional heteroskedasticity remaining.")
    else:
        print("WARNING: Volatility clustering may still be present in residuals.")
    print("\n")

    # 6. NLP Causality (Granger)
    print(f"--- 6. Granger Causality (Sentiment -> Volatility) ---")
    # Does Geopolitics sentiment predict Squared Returns?
    # We test if sentiment adds information to the prediction of volatility (proxied by squared returns)
    for col in sentiment_cols:
        print(f"Testing {col} -> Squared_Returns...")
        data_gc = df[['Log_Return', col]].copy()
        data_gc['Sq_Return'] = data_gc['Log_Return']**2
        try:
            # We check if 'col' Granger-causes 'Sq_Return'
            # maxlag=5 days
            gc_res = grangercausalitytests(data_gc[['Sq_Return', col]], maxlag=5, verbose=False)
            p_values = [round(gc_res[i+1][0]['ssr_ftest'][1], 4) for i in range(5)]
            min_p = min(p_values)
            print(f"  Min p-value (lags 1-5): {min_p}")
            if min_p < 0.05:
                print(f"  Result: {col} shows significant predictive power for volatility.")
            else:
                print(f"  Result: No significant Granger causality detected.")
        except Exception as e:
            print(f"  Could not run GC test: {e}")

    # Visualization of Correlations
    plt.figure(figsize=(10, 8))
    plt.imshow(corr_matrix, cmap='coolwarm', interpolation='nearest')
    plt.colorbar()
    plt.xticks(range(len(sentiment_cols)), sentiment_cols, rotation=45)
    plt.yticks(range(len(sentiment_cols)), sentiment_cols)
    for i in range(len(sentiment_cols)):
        for j in range(len(sentiment_cols)):
            plt.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha='center', va='center')
    plt.title("Sentiment Factor Correlation Matrix")
    os.makedirs("data/output/validation", exist_ok=True)
    plt.savefig("data/output/validation/sentiment_correlation.png")
    plt.close()

    print("\n====================================================")
    print("   VALIDATION COMPLETE - Charts saved to data/output/validation/")
    print("====================================================")


if __name__ == "__main__":
    main()
