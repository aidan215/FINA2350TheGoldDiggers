import pandas as pd
from newspaper import Article
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import random

input_csv = 'data/data_source.csv'
output_csv = 'data/processed/final_dataset.csv'

df = pd.read_csv(input_csv)
print(f"Total rows in dataset: {len(df)}")

processed_urls = set()
if os.path.exists(output_csv):
    try:
        df_out = pd.read_csv(output_csv)
        processed_urls = set(df_out['url'].dropna())
    except:
        pass

# Force reprocessing of empty/failed ones if we want, but for now just process un-processed
to_process = df[~df['url'].isin(processed_urls)]
print(f"Rows remaining to process: {len(to_process)}")

def extract_text(row):
    url = row['url']
    if pd.isna(url): return row, ""
    
    # Random jitter to prevent synchronized hits
    time.sleep(random.uniform(0.5, 1.5)) 
    
    try:
        # Use a more modern browser fingerprint, and random choice
        impersonate_targets = ["chrome120", "edge116", "safari15_5"]
        r = requests.get(url, impersonate=random.choice(impersonate_targets), timeout=20, allow_redirects=True)
        
        if r.status_code != 200:
            return row, ""
            
        a = Article(url)
        a.download(input_html=r.text)
        a.parse()
        
        # Strip boilerplate
        text = a.text.replace("\n", " ").strip()
        
        return row, text
    except Exception:
        return row, ""

os.makedirs('data/processed', exist_ok=True)

# Write header if file doesn't exist
if not os.path.exists(output_csv):
    pd.DataFrame(columns=list(df.columns) + ['News_Context']).to_csv(output_csv, index=False)

success_count = 0
start_time = time.time()

# Lower max_workers to 10
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(extract_text, row) for _, row in to_process.iterrows()]
    
    for i, future in enumerate(as_completed(futures), 1):
        row, text = future.result()
        if len(text) > 200: 
            success_count += 1
        
        row_dict = row.to_dict()
        row_dict['News_Context'] = text
        
        pd.DataFrame([row_dict]).to_csv(output_csv, mode='a', header=False, index=False)
        
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            rem_secs = (len(to_process) - i) / rate
            print(f"Processed {i}/{len(to_process)} | Success: {success_count}/{i} ({(success_count/i)*100:.1f}%) | ETA: {rem_secs/60:.1f} min")

print("Finished extraction from data_source.csv!")
