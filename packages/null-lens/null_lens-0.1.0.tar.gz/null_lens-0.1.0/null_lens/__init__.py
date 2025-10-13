import requests

class NullLens:
    def __init__(self, api_key: str, base_url="https://null-core.ai/api/lens"):
        self.api_key = api_key
        self.base_url = base_url

    def parse(self, text: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {"messages": [{"role": "user", "content": text}]}
        r = requests.post(self.base_url, headers=headers, json=data)
        r.raise_for_status()
        return r.json().get("response")
