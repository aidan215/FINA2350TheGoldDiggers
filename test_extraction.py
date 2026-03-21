import ssl
from newspaper import Article
import requests
from googlenewsdecoder import gnewsdecoder

# Bypass SSL
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

test_url = "https://news.google.com/rss/articles/CBMieEFVX3lxTE0tMWczakdLaEhYVWplN0hWNTRLWDFYSTJONmJ1bTZYc2FkUlZxaVRZMV9YdjIxV1B6Q3hvUUREdlFOQ0h2QThFN0hURGdzRndvUUw4Z1Bybkd4UTl1ZXY4RXlWalFNUHdKMlY2WVNBOGtTWmpnaDNQdw?oc=5"

def test_extraction(url):
    print(f"Testing URL: {url}")
    
    try:
        decoded_result = gnewsdecoder(url)
        final_url = decoded_result.get('decoded_url') if decoded_result.get('status') else url
        print(f"Decoded Source URL: {final_url}")
    except:
        final_url = url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        response = requests.get(final_url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Correct Newspaper4k method: download(input_html=...)
        article = Article(final_url)
        article.download(input_html=html)
        article.parse()
        
        print(f"Final Title: {article.title}")
        print(f"Text length: {len(article.text)}")
        print(f"Text snippet: {article.text[:300]}...")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_extraction(test_url)
