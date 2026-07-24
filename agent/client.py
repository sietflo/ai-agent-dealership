import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
AGENT_USERNAME = os.getenv("AGENT_USERNAME", "admin")
AGENT_PASSWORD = os.getenv("AGENT_PASSWORD", "admin123")

class DealershipAPIClient:
    def __init__(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=10.0)
        self.token = None

    def _login(self):
        response = self.client.post("/auth/login", data={"username": AGENT_USERNAME, "password": AGENT_PASSWORD})
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            raise RuntimeError(f"Failed to authenticate agent: {response.text}")

    def request(self, method: str, url: str, **kwargs):
        if self.token is None:  # Not logged in yet
            self._login()
        res = self.client.request(method, url, **kwargs)
        if res.status_code == 401:  # Token missing/expired, retry once
            self._login()
            res = self.client.request(method, url, **kwargs)
        res.raise_for_status()
        return res.json()

api_client = DealershipAPIClient()