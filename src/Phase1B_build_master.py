import yfinance as yf
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 1. Download Historical Gold Prices (GC=F)
    ticker = "GC=F"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1095)
    
    logger.info(f"Downloading historical data for {ticker} from {start_date.date()} to {end_date.date()}...")
    gold_data = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
    
    if gold_data.empty:
        logger.error(f"Failed to download data for {ticker}")
        return

    # 2. Compute Scaled Logarithmic Returns
    if isinstance(gold_data.columns, pd.MultiIndex):
        close_prices = gold_data['Close'][ticker]
    else:
        close_prices = gold_data['Close']
        
    log_returns = np.log(close_prices / close_prices.shift(1)) * 100
    gold_data['Log_Return'] = log_returns
    
    # 3. Load Sentiment Data
    sentiment_path = "data/processed/autonomous_news_sentiment.csv"
    try:
        sentiment_df = pd.read_csv(sentiment_path)
    except FileNotFoundError:
        logger.error(f"Sentiment data not found at {sentiment_path}. Run Phase 1A first.")
        return

    # 4. Data Preparation for Join
    sentiment_df['Date'] = pd.to_datetime(sentiment_df['Date'])
    
    # Aggregate multiple articles per day
    sentiment_df = sentiment_df.groupby('Date').agg({
        'Monetary': 'mean',
        'Fiscal': 'mean',
        'Geopolitics': 'mean',
        'News_Context': lambda x: " | ".join(x.dropna().astype(str))
    })
    
    # Ensure indices are timezone-naive
    gold_data.index = pd.to_datetime(gold_data.index).tz_localize(None)
    sentiment_df.index = pd.to_datetime(sentiment_df.index).tz_localize(None)

    # Flatten columns if necessary before join to avoid MergeError
    if isinstance(gold_data.columns, pd.MultiIndex):
         gold_data.columns = [col[0] if col[1] == '' or col[1] == ticker else f"{col[0]}_{col[1]}" for col in gold_data.columns]
    
    # 5. Time-Series Alignment (Inner Join)
    # Join the numerical scores AND the News_Context text column
    master_df = gold_data.join(sentiment_df, how='inner')
    
    # 6. Final Cleaning
    sentiment_cols = ['Monetary', 'Fiscal', 'Geopolitics']
    
    # Ensure News_Context is present
    final_cols = ['Close', 'Log_Return', 'Monetary', 'Fiscal', 'Geopolitics', 'News_Context']
    available_cols = [c for c in final_cols if c in master_df.columns]
    master_df = master_df[available_cols]

    output_path = "data/processed/gold_master_data.csv"
    master_df.to_csv(output_path)
    logger.info(f"Successfully exported master data with RAG context to {output_path}")

if __name__ == "__main__":
    main()
