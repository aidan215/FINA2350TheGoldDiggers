import json
import requests
import hashlib
import os
from newspaper import Article
from googlenewsdecoder import gnewsdecoder
from curl_cffi import requests as cur_req

# Constants from scraper
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def diag_extract(rss_url):
    print(f"--- DIAGNOSTICS FOR: {rss_url[:60]}... ---")
    
    # 1. Test Library Decoding
    try:
        decoded = gnewsdecoder(rss_url)
        url = decoded.get('decoded_url') if decoded.get('status') else rss_url
        print(f"1. Library Decoded: {'SUCCESS' if decoded.get('status') else 'FAILED'}")
        print(f"   Target URL: {url[:80]}...")
    except Exception as e:
        print(f"1. Library Error: {e}")
        url = rss_url

    # 2. Test curl_cffi Fetch
    print("2. Testing curl_cffi fetch...")
    try:
        response = cur_req.get(url, impersonate="chrome110", timeout=25, allow_redirects=True)
        print(f"   curl_cffi Status: {response.status_code}")
        print(f"   Final URL: {response.url[:80]}...")
        html = response.text
        print(f"   HTML length: {len(html)}")
    except Exception as e:
        print(f"   curl_cffi FAILED: {e}")
        print("   Falling back to standard requests...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            print(f"   Requests Status: {response.status_code}")
            html = response.text
        except Exception as e2:
            print(f"   Standard Requests also FAILED: {e2}")
            return

    # 3. Test newspaper4k Parsing
    print("3. Testing newspaper4k parsing...")
    try:
        article = Article(url)
        article.download(input_html=html)
        article.parse()
        text = article.text.replace("\n", " ").strip()
        print(f"   Title: {article.title}")
        print(f"   Clean Text Length: {len(text)}")
        print(f"   Snippet: {text[:200]}...")
        
        # 4. Test Quality Gate
        print("4. Testing Quality Gate...")
        if len(text) < 200: 
            print("   REJECTED: Too short (< 200)")
        elif "All rights reserved" in text and len(text) < 500:
            print("   REJECTED: Looks like boilerplate Footer")
        else:
            print("   PASSED quality gate!")
            
    except Exception as e:
        print(f"   Parsing Error: {e}")

if __name__ == "__main__":
    # Test with a real link from Google News
    diag_extract("https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5")
