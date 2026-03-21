import base64
import re

def robust_decode(url):
    try:
        if 'articles/' not in url: return url
        s = url.split('articles/')[1].split('?')[0]
        b = base64.urlsafe_b64decode(s + '==')
        print(f"Outer Decoded Length: {len(b)}")
        # Search for the string that starts with AU_yq
        match = re.search(br'AU_yq[A-Za-z0-9_-]+', b)
        if match:
            inner_b64 = match.group(0).decode('utf-8')
            print(f"Found Inner B64: {inner_b64[:20]}...")
            inner_b = base64.urlsafe_b64decode(inner_b64 + '==')
            print(f"Inner Decoded: {inner_b}")
            urls = re.findall(br'https?://[^\x00-\x1F\x7F-\xFF]+', inner_b)
            if urls: return urls[0].decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
    return url

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
print(f"Final: {robust_decode(url)}")
