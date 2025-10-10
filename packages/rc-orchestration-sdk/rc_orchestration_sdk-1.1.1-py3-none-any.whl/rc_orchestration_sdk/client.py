import os
import json
from typing import Any, Dict, Optional
import requests
import time


class OrchestrationClient:
    def __init__(self, base_url: Optional[str] = None, access_token: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv("ORCH_BASE_URL", "http://localhost:8000/api/v1")
        self.access_token = access_token or os.getenv("ORCH_ACCESS_TOKEN")
        self.api_key = api_key or os.getenv("PUBLIC_API_KEY")

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _public_headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    def _public_base(self) -> str:
        # Convenience: if base is /api/v1, derive /api/public
        if self.base_url.endswith("/api/v1"):
            return self.base_url[:-len("/api/v1")] + "/api/public"
        # If user provided a custom base, expect them to include /api/public fully in methods
        return self.base_url.replace("/api/v1", "/api/public")

    def _request(self, method: str, url: str, **kwargs):
        attempts = 0
        backoff = 0.5
        while True:
            resp = requests.request(method, url, **kwargs)
            if resp.status_code in (429, 500, 502, 503, 504) and attempts < 3:
                time.sleep(backoff)
                backoff *= 2
                attempts += 1
                continue
            resp.raise_for_status()
            return resp

    def login(self, username: str, password: str) -> Dict[str, Any]:
        r = self._request("POST", f"{self.base_url}/auth/login", json={"username": username, "password": password})
        r.raise_for_status()
        data = r.json()
        self.access_token = data.get("access_token")
        return data

    def status(self) -> Dict[str, Any]:
        r = self._request("GET", f"{self.base_url}/orchestration/status", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def run_execution(self, phases: Optional[list[str]] = None, parallel: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        payload = {"phases": phases, "parallel": bool(parallel), "dry_run": bool(dry_run)}
        r = self._request("POST", f"{self.base_url}/orchestration/execute", headers=self._headers(), json=payload)
        r.raise_for_status()
        return r.json()

    # -------- Public API wrappers --------
    def public_status(self) -> Dict[str, Any]:
        url = f"{self._public_base()}/status"
        r = self._request("GET", url, headers=self._public_headers())
        return r.json()

    def public_metrics(self) -> Dict[str, Any]:
        url = f"{self._public_base()}/metrics"
        r = self._request("GET", url, headers=self._public_headers())
        return r.json()

    def public_list_artifacts(self, phase: Optional[str] = None, status_filter: Optional[str] = None, page: int = 1, page_size: int = 50, execution_id: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if phase:
            params["phase"] = phase
        if status_filter:
            params["status_filter"] = status_filter
        if execution_id:
            params["execution_id"] = execution_id
        url = f"{self._public_base()}/artifacts"
        r = self._request("GET", url, headers=self._public_headers(), params=params)
        return r.json()

    def public_sign_artifact(self, artifact_id: str, ttl_seconds: int = 600) -> Dict[str, Any]:
        url = f"{self._public_base()}/artifacts/sign"
        r = self._request("GET", url, headers=self._public_headers(), params={"artifact_id": artifact_id, "ttl_seconds": ttl_seconds})
        return r.json()

    def list_artifacts(self, phase: Optional[str] = None, execution_id: Optional[str] = None, status_filter: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if phase:
            params["phase"] = phase
        if execution_id:
            params["execution_id"] = execution_id
        if status_filter:
            params["status_filter"] = status_filter
        r = self._request("GET", f"{self.base_url}/artifacts", headers=self._headers(), params=params)
        r.raise_for_status()
        return r.json()

    def sign_artifact(self, artifact_id: str) -> Dict[str, Any]:
        r = self._request("GET", f"{self.base_url}/artifacts/{artifact_id}/sign", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def register_webhook(self, url: str, secret: str, events: list[str]) -> Dict[str, Any]:
        r = self._request("POST", f"{self.base_url}/webhooks", headers=self._headers(), params={"url": url, "secret": secret}, json=events)
        r.raise_for_status()
        return r.json()

    def list_webhooks(self) -> list[Dict[str, Any]]:
        r = self._request("GET", f"{self.base_url}/webhooks", headers=self._headers())
        r.raise_for_status()
        return r.json()

    def paginate_artifacts(self, phase: Optional[str] = None, execution_id: Optional[str] = None, status_filter: Optional[str] = None, page_size: int = 50):
        page = 1
        while True:
            params = {"page": page, "page_size": page_size}
            if phase:
                params["phase"] = phase
            if execution_id:
                params["execution_id"] = execution_id
            if status_filter:
                params["status_filter"] = status_filter
            r = self._request("GET", f"{self.base_url}/artifacts", headers=self._headers(), params=params)
            out = r.json()
            arts = out.get('artifacts', [])
            if not arts:
                break
            for a in arts:
                yield a
            if len(arts) < page_size:
                break
            page += 1
