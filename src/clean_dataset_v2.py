import pandas as pd

df = pd.read_csv('data/processed/final_dataset_v2.csv', names=['publish_date', 'url', 'driver_monetary', 'driver_geopolitical', 'driver_fiscal', 'News_Context'])
# Drop the header row if it got mixed in
df = df[df['publish_date'] != 'publish_date']

# Filter out empty or short contexts
df['News_Context'] = df['News_Context'].fillna('')
df_clean = df[df['News_Context'].str.len() > 200].copy()

# Rename columns to match the previous naming convention expected by Phase 2
df_clean = df_clean.rename(columns={
    'publish_date': 'Date',
    'driver_monetary': 'Monetary',
    'driver_geopolitical': 'Geopolitics',
    'driver_fiscal': 'Fiscal'
})

# Ensure Date is in correct format (YYYY-MM-DD)
df_clean['Date'] = pd.to_datetime(df_clean['Date']).dt.strftime('%Y-%m-%d')

print(f"Total valid articles: {len(df_clean)}")
df_clean.to_csv('data/processed/autonomous_news_sentiment.csv', index=False)
print("Saved to data/processed/autonomous_news_sentiment.csv")
