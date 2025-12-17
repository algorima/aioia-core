from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


def _parse_keys() -> List[str]:
    """Parse SerpAPI keys from env.

    Priority:
      1) SERPAPI_KEYS="k1,k2,k3"
      2) SERPAPI_KEY="single_key"
    """
    keys = os.getenv("SERPAPI_KEYS", "").strip()
    if keys:
        return [k.strip() for k in keys.split(",") if k.strip()]
    k = os.getenv("SERPAPI_KEY", "").strip()
    return [k] if k else []


@dataclass
class SerpApiRotator:
    """Simple SerpAPI client with key rotation."""

    keys: Optional[List[str]] = None
    base_url: str = "https://serpapi.com/search"
    timeout_s: int = 60
    rotate_sleep_s: float = 0.5

    def __post_init__(self):
        self.keys = self.keys or _parse_keys()
        if not self.keys:
            raise ValueError("SERPAPI_KEY or SERPAPI_KEYS is not set.")
        self._idx = 0

    @property
    def current_key(self) -> str:
        return self.keys[self._idx]

    def _rotate(self) -> None:
        self._idx = (self._idx + 1) % len(self.keys)
        time.sleep(self.rotate_sleep_s)

    def _looks_like_quota_error(self, payload: Any) -> bool:
        if not isinstance(payload, dict):
            return False
        err = str(payload.get("error", "")).lower()
        return any(x in err for x in ["quota", "limit", "exceed", "exceeded", "billing"])

    def search(self, params: Dict[str, Any], max_key_tries: Optional[int] = None) -> Dict[str, Any]:
        """Call SerpAPI, rotating keys on quota/rate-limit errors.

        params should NOT include api_key; we inject it.
        """
        max_key_tries = max_key_tries or len(self.keys)
        last_err: Optional[str] = None

        for _ in range(max_key_tries):
            p = dict(params)
            p["api_key"] = self.current_key

            try:
                r = requests.get(self.base_url, params=p, timeout=self.timeout_s)
            except requests.RequestException as e:
                last_err = f"request_error: {e}"
                self._rotate()
                continue

            if r.status_code == 429:
                last_err = "http_429_rate_limited"
                self._rotate()
                continue

            try:
                data = r.json()
            except Exception:
                last_err = f"non_json_response status={r.status_code}"
                self._rotate()
                continue

            if r.status_code >= 400:
                last_err = f"http_{r.status_code}"
                self._rotate()
                continue

            if self._looks_like_quota_error(data):
                last_err = f"quota_error: {data.get('error')}"
                self._rotate()
                continue

            return data

        raise RuntimeError(f"SerpAPI failed after {max_key_tries} key-tries. last_err={last_err}")
