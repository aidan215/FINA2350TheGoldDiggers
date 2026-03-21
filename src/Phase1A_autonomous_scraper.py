import os
import asyncio
import json
import logging
import pandas as pd
import ssl
import urllib.parse
import sys
import hashlib
import requests
from datetime import datetime, timedelta
from google import genai
from dotenv import load_dotenv
from newspaper import Article
from curl_cffi import requests as cur_req
import time

# Bypass SSL
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DAYS_TO_SCRAPE = 1095
CHUNK_SIZE_DAYS = 7
BATCH_SIZE = 20
SAFE_RPM_DELAY = 0.5 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Optimized for GDELT syntax
QUERIES = [
    '"Gold market"', '"Federal Reserve" "interest rates"', "inflation economy", 
    '"Central Bank" gold', "Geopolitics risk", '"Recession probability"'
]

MODEL_NAME = 'gemini-3.1-flash-lite-preview'

async def extract_full_text_async(url, date_str):
    try:
        try:
            response = cur_req.get(url, impersonate="chrome110", timeout=25, allow_redirects=True)
            html = response.text
        except:
            response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            html = response.text

        article = Article(url)
        article.download(input_html=html)
        article.parse()
        
        text = article.text.replace("\n", " ").strip()
        
        if len(text) < 200: return None
        if "All rights reserved" in text and len(text) < 500: return None
        if "This material may not be published" in text and len(text) < 500: return None

        url_hash = hashlib.md5(url.encode()).hexdigest()
        raw_dir = f"data/raw/{date_str}"
        os.makedirs(raw_dir, exist_ok=True)
        with open(os.path.join(raw_dir, f"{url_hash}.html"), "w", encoding="utf-8") as f:
            f.write(html)
            
        return text
    except: return None

async def filter_headlines(client, articles):
    if not articles: return []
    prompt = f"Identify relevant Macro/Gold/Finance headline IDs: {json.dumps([{'id':i, 't':a['title']} for i,a in enumerate(articles)])}. Output strictly a JSON array."
    try:
        response = await client.aio.models.generate_content(model=MODEL_NAME, contents=prompt, config={'response_mime_type': 'application/json'})
        relevant_ids = json.loads(response.text)
        return [articles[i] for i in relevant_ids if isinstance(i, int) and i < len(articles)]
    except: return articles[:3]

async def get_batch_sentiment(client, articles):
    batch_text = ""
    for i, art in enumerate(articles):
        batch_text += f"ID:{i} | TEXT: {art['text'][:2000]}\n---\n"

    prompt = f"Score these Gold-related articles. Return strictly a JSON ARRAY of objects with keys: 'id', 'monetary', 'fiscal', 'geopolitics'. Floats -1.0 to 1.0. Articles: {batch_text}"

    try:
        response = await client.aio.models.generate_content(model=MODEL_NAME, contents=prompt, config={'response_mime_type': 'application/json'})
        scores = json.loads(response.text)
        results = []
        for s in scores:
            idx = int(s['id'])
            if idx < len(articles):
                art = articles[idx]
                results.append({'Date': art['date'], 'monetary': float(s.get('monetary', 0.0)), 'fiscal': float(s.get('fiscal', 0.0)), 
                                'geopolitics': float(s.get('geopolitics', 0.0)), 'Full_Text': art['text'], 'PK': art['pk']})
        return results
    except: return []

async def fetch_gdelt_with_retry(url, max_retries=5):
    """Fetch from GDELT with exponential backoff for 429 Too Many Requests."""
    for attempt in range(max_retries):
        try:
            gdelt_resp = requests.get(url, headers=HEADERS, timeout=30)
            if gdelt_resp.status_code == 200:
                try:
                    data = gdelt_resp.json()
                    return data.get('articles', [])
                except json.JSONDecodeError:
                    logger.error(f"GDELT_NOT_JSON|Skipping week")
                    return []
            elif gdelt_resp.status_code == 429:
                wait_time = 10 * (2 ** attempt) # 10s, 20s, 40s...
                logger.warning(f"GDELT API Rate Limit Hit (429). Sleeping {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"GDELT HTTP {gdelt_resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"GDELT_NETWORK_ERROR|{e}")
            await asyncio.sleep(5)
    return []

async def main():
    client = genai.Client(api_key=GEMINI_API_KEY)
    os.makedirs("data/processed", exist_ok=True)
    raw_path = "data/processed/raw_article_scores.csv"
    
    processed_pks = set()
    scored_data = []
    if os.path.exists(raw_path):
        try:
            df = pd.read_csv(raw_path)
            scored_data = df.to_dict('records')
            processed_pks = set(df['PK'].unique())
            logger.info(f"RESUME|Articles:{len(scored_data)}")
        except: pass

    end_global = datetime.now()
    start_global = end_global - timedelta(days=DAYS_TO_SCRAPE)

    for q in QUERIES:
        curr = start_global
        while curr < end_global:
            nxt = curr + timedelta(days=CHUNK_SIZE_DAYS)
            pk = f"{q}|{curr.strftime('%Y-%m-%d')}"
            if pk in processed_pks: 
                curr = nxt
                continue

            logger.info(f"STARTING|{pk}")
            
            # GDELT specific parameters
            query_str = f'({q}) sourcelang:eng'
            encoded_q = urllib.parse.quote(query_str)
            start_str = curr.strftime('%Y%m%d%H%M%S')
            end_str = nxt.strftime('%Y%m%d%H%M%S')
            
            url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={encoded_q}&mode=artlist&maxrecords=50&format=json&startdatetime={start_str}&enddatetime={end_str}"
            
            articles_data = await fetch_gdelt_with_retry(url)
            
            entries = []
            for a in articles_data:
                pub_date = curr.strftime("%Y-%m-%d")
                try:
                    if 'seendate' in a:
                        pub_date = datetime.strptime(a['seendate'], "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
                except: pass
                entries.append({'title': a.get('title', ''), 'link': a.get('url', ''), 'published': pub_date})
            
            if not entries:
                logger.info(f"FILTER|Query:{q}|Total:0|Relevant:0")
                processed_pks.add(pk)
                curr = nxt
                await asyncio.sleep(2) # Base delay between successful requests
                continue
                
            relevant = await filter_headlines(client, entries)
            logger.info(f"FILTER|Query:{q}|Total:{len(entries)}|Relevant:{len(relevant)}")

            tasks = [extract_full_text_async(art['link'], art['published']) for art in relevant]
            texts = await asyncio.gather(*tasks)
            
            batch = []
            for art, txt in zip(relevant, texts):
                if not txt: continue
                batch.append({'text': txt, 'date': art['published'], 'pk': pk})

            for i in range(0, len(batch), BATCH_SIZE):
                res = await get_batch_sentiment(client, batch[i:i+BATCH_SIZE])
                if res:
                    scored_data.extend(res)
                    df_raw = pd.DataFrame(scored_data)
                    df_raw.to_csv(raw_path, index=False)
                    cols = ['monetary', 'fiscal', 'geopolitics']
                    daily = df_raw.groupby('Date')[cols].mean()
                    daily['News_Context'] = df_raw.groupby('Date')['Full_Text'].apply(lambda x: " | ".join(filter(None, map(str, x))))
                    daily.rename(columns={'monetary':'Monetary','fiscal':'Fiscal','geopolitics':'Geopolitics'}, inplace=True)
                    daily.to_csv("data/processed/autonomous_news_sentiment.csv")
                    logger.info(f"DATA_UPDATE|Articles:{len(df_raw)}|Latest:{res[-1]['Date']}")
                await asyncio.sleep(SAFE_RPM_DELAY)

            processed_pks.add(pk)
            curr = nxt
            await asyncio.sleep(2) # Base delay between successful GDELT requests

    with open("data/processed/DONE_SCRAPING.txt", "w") as f: f.write(f"Done at {datetime.now()}")
    logger.info("FINISHED_ALL")

if __name__ == "__main__": asyncio.run(main())
