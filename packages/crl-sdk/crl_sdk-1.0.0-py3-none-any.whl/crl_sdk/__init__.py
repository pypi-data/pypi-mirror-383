"""CRL Technologies API Client - Official Python SDK"""
import requests
import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional

class CRLClient:
    """Client for CRL Technologies API"""
    
    def __init__(self, api_url: str, tenant_id: str, api_key: str, timeout: int = 30):
        self.api_url = api_url.rstrip('/')
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.timeout = timeout
        
    def _generate_signature(self, payload: Dict[str, Any]) -> tuple:
        timestamp = str(int(time.time()))
        message = f"{timestamp}{json.dumps(payload, separators=(',', ':'))}"
        signature = hmac.new(
            self.api_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature, timestamp
    
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.api_url}{endpoint}"
        headers = {"X-Tenant-ID": self.tenant_id}
        
        if payload:
            signature, timestamp = self._generate_signature(payload)
            headers.update({
                "X-Signature": signature,
                "X-Timestamp": timestamp,
                "Content-Type": "application/json"
            })
        
        response = requests.request(method=method, url=url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        return self._make_request("GET", "/health")
    
    def calculate_crl(self, initial_margin: float, exposure_value: float, direction: str, mode: str = "crl") -> Dict[str, Any]:
        payload = {"initial_margin": initial_margin, "exposure_value": exposure_value, "direction": direction, "mode": mode}
        return self._make_request("POST", "/v1/calc", payload)
