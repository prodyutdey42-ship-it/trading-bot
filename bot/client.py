import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from bot.logging_config import setup_logger

load_dotenv()
logger = setup_logger()

TESTNET_BASE_URL =  "https://demo-fapi.binance.com"
class TestnetClient:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = TESTNET_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        })

    def _sign(self, params):
        query = "&".join(f"{k}={v}" for k, v in params.items())
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def futures_create_order(self, **kwargs):
        params = {**kwargs}
        params["timestamp"] = int(time.time() * 1000)
        params = self._sign(params)

        url = f"{self.base_url}/fapi/v1/order"
        logger.info(f"POST {url} | Params: { {k:v for k,v in params.items() if k != 'signature'} }")

        response = self.session.post(url, data=params)
        data = response.json()

        if "code" in data and data["code"] != 200:
            logger.error(f"API error: {data}")
            raise Exception(f"APIError(code={data['code']}): {data.get('msg', 'Unknown error')}")

        return data


def get_client():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API keys not found. Check your .env file.")
        raise EnvironmentError("Missing API keys in .env")

    logger.info("Testnet client initialized successfully.")
    return TestnetClient(api_key, api_secret)