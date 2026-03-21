import os
import asyncio
from google import genai
from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv()

async def gemini_decode():
    url = "https://news.google.com/rss/articles/CBMiogFBVV95cUxOMk1pZ01rQ3NTcXAyZ1NHUGQybVlJckpxdWZmSmE0RkJHLXFkd3FIVkdlZFZhc0FaWm1pMkN6UU1BWkNPakI3WEVrXzFMaEhxcTd5d2dVUEoxdE82S29aRVdDS1pxRWR3TlJwVHFSUERyeEhaSXpGMC1mN0RMZXA1UDNpbHk0aDlKOHluTml3WGF5ZktXTUlKZHV4Ty00RVJlSGfSAacBQVVfeXFMT2Jra0x6c3RBVERkSzRwV3hUWnI0Z0VoSkV5TmhjR3ZUTUhQcEcySXM4dTJBSmlSdEFGWlRwMlhJMlFJMDVDMTF1MEZzSmlJcEZ6UVRnRVdZVFlCb2ljdjFTZkY0Q2FnTWJTNmxJM0pPQ3VDd011Q2p6MVh5cGhEcWpxNF9vb0NkbnZabHl6M2tUeTF5UnpfUGFIYmV4U3ktMjFWQ25MMlU?oc=5"
    r = requests.get(url, impersonate="chrome110", timeout=10)
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"Find the original news article URL in this Google News page HTML. Look for non-google links. Return ONLY the URL. HTML: {r.text[:10000]}"
    
    response = await client.aio.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    print(f"Gemini says: {response.text}")

if __name__ == "__main__":
    asyncio.run(gemini_decode())
