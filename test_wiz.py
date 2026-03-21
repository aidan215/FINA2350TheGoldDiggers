from curl_cffi import requests
import re

def wiz_decode(url):
    try:
        r = requests.get(url, impersonate="chrome110", timeout=10)
        # Look for AF_initDataCallback
        # The data is often in a format like [null,null,["http://..."]]
        urls = re.findall(r'https?://[^\s\\<>"]+', r.text)
        for u in urls:
            if "google.com" not in u and "gstatic.com" not in u and "googleusercontent.com" not in u:
                return u
    except Exception as e:
        print(f"Error: {e}")
    return url

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
print(f"Final: {wiz_decode(url)}")
