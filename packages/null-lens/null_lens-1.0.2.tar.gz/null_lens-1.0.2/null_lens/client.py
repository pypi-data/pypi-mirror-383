import os
import requests

class NullLensResponse:
    """Structured response object for Null Lens API."""

    def __init__(self, text: str):
        self.raw = text
        self.motive = self._extract("[motive]")
        self.scope = self._extract("[scope]")
        self.priority = self._extract("[priority]")

    def _extract(self, prefix: str):
        for line in self.raw.splitlines():
            if line.lower().startswith(prefix):
                return line.split("]", 1)[1].strip()
        return None

    def __repr__(self):
        return (
            f"<NullLens motive={self.motive!r}, "
            f"scope={self.scope!r}, priority={self.priority!r}>"
        )


class NullLens:
    """Python client for Null Lens API."""

    def __init__(self, api_key=None, base_url="https://null-core.ai/api/lens"):
        self.api_key = api_key or os.getenv("NULL_LENS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Missing API key. Pass api_key or set NULL_LENS_API_KEY environment variable."
            )
        self.base_url = base_url

    def parse(self, text: str) -> NullLensResponse:
        """Send a single text input and return a structured 3-line response."""
        payload = {"messages": [{"role": "user", "content": text}]}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        res = requests.post(self.base_url, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        return NullLensResponse(data["response"])
