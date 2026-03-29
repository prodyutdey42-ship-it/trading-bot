import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

print(f"API Key loaded: {API_KEY[:10]}..." if API_KEY else "❌ API Key NOT found")
print(f"Secret loaded: {API_SECRET[:10]}..." if API_SECRET else "❌ Secret NOT found")

# Test 1: Check server time
print("\n--- Test 1: Server Time ---")
r = requests.get("https://testnet.binancefuture.com/fapi/v1/time")
print(r.json())

# Test 2: Check account (requires auth)
print("\n--- Test 2: Account Info ---")
params = {"timestamp": int(time.time() * 1000)}
query = "&".join(f"{k}={v}" for k, v in params.items())
signature = hmac.new(
    API_SECRET.encode("utf-8"),
    query.encode("utf-8"),
    hashlib.sha256
).hexdigest()
params["signature"] = signature

headers = {"X-MBX-APIKEY": API_KEY}
r = requests.get(
    "https://testnet.binancefuture.com/fapi/v2/account",
    params=params,
    headers=headers
)
print(r.json())