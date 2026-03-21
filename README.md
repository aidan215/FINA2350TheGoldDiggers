# FINA2350: The Gold Diggers

This repository contains the data extraction and econometric modeling pipeline for our FINA2350 project on Gold Futures (GC=F) volatility. The project compares a baseline GARCH model against an NLP-augmented GARCH-X model and prepares data for a narrative-based Retrieval-Augmented Generation (RAG) analysis.

## Project Structure

- `src/`
  - `Phase1A_extract_articles.py`: The robust extraction script that pulls full-text articles from our curated list (`data_source.csv`), bypassing soft paywalls using `curl_cffi` and `newspaper4k`.
  - `Phase1B_build_master.py`: Merges the NLP sentiment dataset with historical GC=F market data from Yahoo Finance, aggregating news context by trading day.
  - `Phase2_run_models.py`: Fits the Baseline GARCH(1,1) and NLP-Augmented GARCH-X(1,1) models, and generates the final volatility charts and RAG dataset.
  - `Progress_monitor.py`: A real-time terminal dashboard to track extraction progress.
- `data/`
  - `data_source.csv`: Our curated starting list of 6,400+ macro/financial news URLs.
  - `processed/gold_master_data.csv`: The perfectly aligned 36-month timeline merging GC=F prices, daily sentiment scores (Monetary, Fiscal, Geopolitics), and full article text.
  - `output/fina2350_master_dataset_for_rag.csv`: **(THIS IS THE ONLY FILE YOU NEED FOR THE LLM/RAG PHASE)**. The final, master dataset containing everything in `gold_master_data.csv` PLUS the computed conditional volatilities from both GARCH models. 
  - `output/volatility_comparison.png`: A visual comparison of the Baseline vs. NLP-Augmented volatility.

## Pipeline Overview

### Phase 1: High-Fidelity Data Extraction
We experienced significant issues with Google News obfuscation and publisher anti-bot firewalls. To solve this, we used a curated CSV of URLs and ran a highly optimized extraction pipeline:
- **Bypassing Firewalls:** Used `curl_cffi` to spoof Chrome/Edge/Safari TLS fingerprints to bypass Cloudflare and soft paywalls.
- **Extraction:** Used `newspaper4k` to parse the raw HTML and extract the core article text.
- **Quality Gate:** Strict filtering to remove boilerplate (e.g., copyright notices) and articles under 200 characters.
- **Result:** Successfully rescued and extracted **3,252 high-quality full-text articles** spanning exactly 36 months (March 2023 - Feb 2026).

### Phase 1B: Market Data Synchronization
The extracted news dataset was aggregated by `Date` (averaging sentiment scores and concatenating `News_Context`) and inner-joined with historical Gold Futures (GC=F) log returns downloaded via `yfinance`. This resulted in a perfect 687-trading-day continuous timeline.

### Phase 2: Econometric Modeling
Using the `arch` library, we fitted two models:
1. **Baseline GARCH(1,1):** Captured the standard volatility clustering of Gold.
2. **NLP-Augmented GARCH-X(1,1):** Integrated our three sentiment factors (`Monetary`, `Fiscal`, `Geopolitics`) into the mean equation to test if exogenous narrative shocks improve volatility prediction.

## Next Steps for the Group
The heavy lifting for data engineering and econometric modeling is complete.
1. Review the `volatility_comparison.png` chart to see the model differences.
2. Use **`data/output/fina2350_master_dataset_for_rag.csv`** for the RAG pipeline. It contains the exact `News_Context` for every trading day alongside the market volatility, making it perfectly formatted for LLM ingestion.
