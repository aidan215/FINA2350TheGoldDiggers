import requests as reqs
import re

def decode_google_news_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = reqs.get(url, headers=headers, allow_redirects=True, timeout=10)
        print(f"Status: {r.status_code}")
        # Check for window.location
        match = re.search(r'window\.location\.href\s*=\s*"(.*?)"', r.text)
        if match:
            print(f"Found window.location: {match.group(1)}")
            return match.group(1)
        # Check for meta refresh
        match = re.search(r'url=(https?://[^\s<>"]+)', r.text)
        if match:
            print(f"Found meta refresh: {match.group(1)}")
            return match.group(1)
        # Check for data-n-a-id link
        match = re.search(r'data-n-a-id="(.*?)"', r.text)
        if match:
            print(f"Found data-n-a-id: {match.group(1)}")
            # This is the CBM string again... not the URL.
    except Exception as e:
        print(f"Error: {e}")
    return url

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
print(f"Result: {decode_google_news_url(url)}")
