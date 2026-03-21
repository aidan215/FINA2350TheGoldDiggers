import pandas as pd
from newspaper import Article
from curl_cffi import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import random

input_csv = 'data/processed/final_dataset.csv'
output_csv = 'data/processed/final_dataset_v2.csv'

df = pd.read_csv(input_csv)
print(f"Total rows in dataset: {len(df)}")

# Identify rows where News_Context is missing, NaN, or too short
failed_mask = df['News_Context'].isna() | (df['News_Context'].str.len() < 200)
to_process = df[failed_mask]
already_success = df[~failed_mask]

print(f"Already successful: {len(already_success)}")
print(f"Rows to reprocess: {len(to_process)}")

def extract_text(row):
    url = row['url']
    if pd.isna(url): return row, ""
    
    # Random jitter to prevent synchronized hits
    time.sleep(random.uniform(0.5, 2.5)) 
    
    try:
        # Use a more modern browser fingerprint, and random choice
        impersonate_targets = ["chrome120", "edge116", "safari15_5"]
        r = requests.get(url, impersonate=random.choice(impersonate_targets), timeout=30, allow_redirects=True)
        
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

# Start output with already successful ones
already_success.to_csv(output_csv, index=False)

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
        
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            rem_secs = (len(to_process) - i) / rate
            print(f"Processed {i}/{len(to_process)} | Rescued: {success_count}/{i} ({(success_count/i)*100:.1f}%) | ETA: {rem_secs/60:.1f} min")

print("Finished re-extraction!")
