import base64
import re
import requests
from newspaper import Article

def local_decode_gnews(url):
    try:
        if 'articles/' not in url: return url
        s = url.split('articles/')[1].split('?')[0]
        b = base64.urlsafe_b64decode(s + '==')
        match = re.search(br'AU_yq[A-Za-z0-9_-]+', b)
        if match:
            inner_b64 = match.group(0).decode('utf-8')
            inner_b = base64.urlsafe_b64decode(inner_b64 + '==')
            urls = re.findall(br'https?://[^\x00-\x1F\x7F-\xFF]+', inner_b)
            if urls: return urls[0].decode('utf-8')
    except: pass
    return url

def test_extract():
    test_urls = [
        "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5",
        "https://news.google.com/rss/articles/CBMi0AFBVV95cUxOc01NbFdLYUhVTU51ODE1V01rQ1Z1Ql8tUFZyQ0t6b3RZSWh3X0F6QW8wNHdLMkJaaHNWOTZ4RDFTVGpncEFRTlhVUG1ZSHoxdlVKSlp5WkdHN1JfQ251R1JFbmQtdjkydU9kUmJYc1dqQTlrSjZiZEtpZ0N3cEY3TkJBN0M5MmVPbFRhaVM5UVFodjRVMnBfeWJjYmZ5dWFYZmFUUnJKVUJnMHMtM1dTTFNQSzlEOUNsUmFESVI5N0lLNWR5V3Q2MEFiV0lEeTBX"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for u in test_urls:
        decoded = local_decode_gnews(u)
        print(f"URL: {u[:50]}... -> {decoded[:50]}...")
        if "news.google.com" in decoded:
            print("FAILED DECODE")
            continue
        try:
            r = requests.get(decoded, headers=headers, timeout=15)
            print(f"Fetch Status: {r.status_code}")
            a = Article(decoded)
            a.download(input_html=r.text)
            a.parse()
            print(f"Text Length: {len(a.text)}")
            print(f"Snippet: {a.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_extract()
