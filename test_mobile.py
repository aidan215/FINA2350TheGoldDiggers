from curl_cffi import requests

def test_mobile(url):
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'}
    try:
        r = requests.get(url, headers=headers, impersonate="chrome110", timeout=10, allow_redirects=True)
        print(f"Status: {r.status_code}")
        print(f"Final URL: {r.url}")
        if "google.com" not in r.url:
            print("BINGO! Redirected as Mobile.")
        else:
            print("Still on Google.")
    except Exception as e:
        print(f"Error: {e}")

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
test_mobile(url)
