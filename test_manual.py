import base64
import re

def manual_decode(url):
    match = re.search(r'articles/(.*?)\?', url)
    if not match:
        match = re.search(r'articles/(.*)', url)
    
    if match:
        encoded = match.group(1)
        # Pad with =
        padding = len(encoded) % 4
        if padding:
            encoded += "=" * (4 - padding)
        try:
            decoded = base64.urlsafe_b64decode(encoded)
            # Find the first occurrence of http
            decoded_str = decoded.decode('utf-8', errors='ignore')
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', decoded_str)
            return urls[0] if urls else None
        except Exception as e:
            print(f"B64 Error: {e}")
    return None

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
print(f"Decoded: {manual_decode(url)}")
