import feedparser
from curl_cffi import requests
import urllib.parse
import re

def test_redirect():
    q = urllib.parse.quote("Gold market news")
    rss_url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    
    response = requests.get(rss_url, impersonate="chrome110", timeout=15)
    feed = feedparser.parse(response.text)
    
    if not feed.entries:
        print("No entries")
        return
    
    url = feed.entries[0].link
    print(f"Testing Link: {url}")
    
    # Try fetching with allow_redirects=True
    resp = requests.get(url, impersonate="chrome110", timeout=15, allow_redirects=True)
    print(f"Status: {resp.status_code}")
    print(f"Final URL: {resp.url}")
    
    if "news.google.com" in resp.url:
        print("Still on Google News. Looking for redirect link in body...")
        # Look for any link that looks like the real destination
        links = re.findall(r'href="(http.*?)"', resp.text)
        for l in links:
            if "news.google.com" not in l and "google.com" not in l:
                print(f"Found potential destination: {l}")
                break
    else:
        print("Redirected successfully!")

if __name__ == "__main__":
    test_redirect()
