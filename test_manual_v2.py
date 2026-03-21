import base64
import re

def manual_decode_v2(url):
    try:
        if 'articles/' not in url: return url
        b64_str = url.split('articles/')[1].split('?')[0]
        # Padding
        b64_str += '=' * (-len(b64_str) % 4)
        decoded = base64.urlsafe_b64decode(b64_str)
        # Search for the first http link in the decoded binary
        # Google News CBM often has the URL at the end of the binary
        pattern = re.compile(br'https?://[^\x00-\x1F\x7F-\xFF]+')
        match = pattern.search(decoded)
        if match:
            return match.group(0).decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
    return url

url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
print(f"Decoded: {manual_decode_v2(url)}")
