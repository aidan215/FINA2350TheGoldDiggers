import requests
import json
from newspaper import Article
from curl_cffi import requests as cur_req

def test_gdelt():
    print("--- TESTING GDELT API ---")
    # GDELT 2.0 DOC API endpoint
    # Querying for Gold and (Federal Reserve OR Inflation)
    # Using exact date range: March 1, 2023 to March 7, 2023
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc?"
        "query=(gold OR \"gold market\") (inflation OR reserve OR economy) sourcelang:eng&"
        "mode=artlist&"
        "maxrecords=10&"
        "format=json&"
        "startdatetime=20230301000000&"
        "enddatetime=20230307000000"
    )
    
    try:
        print(f"Requesting GDELT URL: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"Found {len(articles)} articles from GDELT.\n")
        
        for i, art in enumerate(articles[:3]):
            print(f"[{i+1}] Title: {art.get('title')}")
            print(f"    Direct URL: {art.get('url')}")
            print(f"    Date: {art.get('seendate')}")
            
            # Test our curl_cffi + newspaper4k extraction pipeline
            try:
                # Fetch
                print("    Fetching HTML...")
                html_resp = cur_req.get(art.get('url'), impersonate="chrome110", timeout=15, allow_redirects=True)
                # Parse
                print("    Parsing with newspaper4k...")
                article_obj = Article(art.get('url'))
                article_obj.download(input_html=html_resp.text)
                article_obj.parse()
                
                text = article_obj.text.replace("\n", " ").strip()
                print(f"    Extracted Text Length: {len(text)}")
                print(f"    Snippet: {text[:150]}...\n")
                
            except Exception as e:
                print(f"    Extraction Failed: {e}\n")
                
    except Exception as e:
        print(f"GDELT API Error: {e}")

if __name__ == "__main__":
    test_gdelt()
