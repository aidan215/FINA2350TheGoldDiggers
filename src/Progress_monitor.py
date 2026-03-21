import os
import time
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import re

# Mirror the queries from the scraper for accurate unit calculation
QUERIES = [
    "Gold", "Federal Reserve", "inflation", 
    "Central Bank", "Geopolitics", "Recession"
]

def get_process_status():
    try:
        output = subprocess.check_output(["ps", "aux"])
        if b"Phase1A_autonomous_scraper.py" in output:
            return "\033[92mRUNNING\033[0m"
        return "\033[91mSTOPPED\033[0m"
    except:
        return "UNKNOWN"

def get_latest_stats():
    status = {"query": None, "date": None, "articles": 0, "start_time": None}
    if not os.path.exists("scraper.log"): return status
    
    try:
        # Get script start time from log file creation or first entry
        status["start_time"] = os.path.getmtime("scraper.log")
        
        with open("scraper.log", "r") as f:
            lines = f.readlines()[-300:]
            for line in reversed(lines):
                # Match STARTING|Query|YYYY-MM-DD
                start_match = re.search(r"STARTING\|(.*?)\|([\d-]+)", line)
                if start_match and not status["date"]:
                    status["query"] = start_match.group(1)
                    status["date"] = datetime.strptime(start_match.group(2), "%Y-%m-%d")
                
                # DATA_UPDATE|Articles:X
                update_match = re.search(r"DATA_UPDATE\|Articles:(\d+)", line)
                if update_match and status["articles"] == 0:
                    status["articles"] = int(update_match.group(1))
    except: pass
    return status

def main():
    total_days_per_query = 1095
    total_queries = len(QUERIES)
    total_units = total_queries * total_days_per_query
    
    reference_now = datetime(2026, 3, 21)
    start_date_global = reference_now - timedelta(days=total_days_per_query)
    
    start_wall_time = time.time()
    
    print("\033[H\033[J") # Clear screen

    while True:
        status_str = get_process_status()
        stats = get_latest_stats()
        
        progress_pct = 0
        time_rem = "Calculating..."
        
        if stats["query"] in QUERIES and stats["date"]:
            q_idx = QUERIES.index(stats["query"])
            days_in_q = (stats["date"] - start_date_global).days
            
            units_done = (q_idx * total_days_per_query) + days_in_q
            progress_pct = min(100, max(0, (units_done / total_units) * 100))
            
            # ETA Calculation
            elapsed = time.time() - start_wall_time
            if progress_pct > 0.1:
                total_est_time = (elapsed / progress_pct) * 100
                rem_seconds = total_est_time - elapsed
                time_rem = str(timedelta(seconds=int(rem_seconds)))

        # Terminal UI
        print(f"\033[H") 
        print("="*60)
        print(f" FINA2350 PRODUCTION DASHBOARD | PAID TIER 1")
        print("="*60)
        print(f" STATUS: {status_str}")
        print(f" TOTAL ARTICLES SCORED: {stats['articles']}")
        print(f" CURRENT QUERY: {stats['query']} ({QUERIES.index(stats['query'])+1 if stats['query'] in QUERIES else '?'}/{total_queries})")
        
        if stats["date"]:
            print(f" TIMELINE: {stats['date'].strftime('%Y-%m-%d')} (Started Mar 2023)")
        else:
            print(f" TIMELINE: Initializing extraction...")
            
        # Unified Progress Bar
        bar_len = 40
        filled_len = int(bar_len * progress_pct / 100)
        bar = '█' * filled_len + '-' * (bar_len - filled_len)
        print(f" TOTAL PROGRESS: |{bar}| {progress_pct:.2f}%")
        print(f" EST. TIME REMAINING: {time_rem}")
        print("="*60)
        print(f" LOGS: Raw HTML Saved to data/raw/ | Option B Active")
        print(f" Refresh: 10s | {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        if os.path.exists("data/processed/DONE_SCRAPING.txt"):
            print("\n\033[92mCOMPLETED! FINAL DATASET READY.\033[0m")
            break
            
        time.sleep(10)

if __name__ == "__main__":
    main()
