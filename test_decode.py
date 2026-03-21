import googlenewsdecoder
import feedparser
from curl_cffi import requests
import urllib.parse

def test_decode():
    q = urllib.parse.quote("Gold market news")
    rss_url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    
    # Use curl_cffi for RSS too
    response = requests.get(rss_url, impersonate="chrome110", timeout=15)
    print(f"RSS Status: {response.status_code}")
    
    feed = feedparser.parse(response.text)
    if not feed.entries:
        print("No entries found in feed")
        return
    
    test_entry = feed.entries[0]
    print(f"Original Link: {test_entry.link}")
    
    try:
        # Note: googlenewsdecoder might need the link to be a certain format
        decoded = googlenewsdecoder.gnewsdecoder(test_entry.link)
        print(f"Decoded Status: {decoded.get('status')}")
        print(f"Decoded URL: {decoded.get('decoded_url')}")
        
        target_url = decoded.get('decoded_url') if decoded.get('status') else test_entry.link
        
        # Test final fetch
        final_resp = requests.get(target_url, impersonate="chrome110", timeout=15, follow_redirects=True)
        print(f"Final Status: {final_resp.status_code}")
        print(f"Final URL: {final_resp.url}")
        print(f"HTML Length: {len(final_resp.text)}")
        print(f"Title: {final_resp.text.split('<title>')[1].split('</title>')[0] if '<title>' in final_resp.text else 'No Title'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_decode()
