"""CRL API Python client."""

import time
import json
import uuid
from typing import Optional
from urllib.parse import urljoin
import requests

from .auth import create_signature
from .models import CalcRequest, CalcResponse, ProductMode, Side
from .exceptions import (
    AuthenticationError, ValidationError, RateLimitError,
    ConflictError, NotFoundError, ServerError, CRLAPIError
)


class CRLClient:
    """CRL White Label API client."""
    
    def __init__(self, key_id: str, secret: str, base_url: str = "https://api.crl.example/v1"):
        """Initialize CRL API client."""
        self.key_id = key_id
        self.secret = secret
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _create_headers(self, method: str, path: str, body: str = "") -> dict:
        """Create request headers with HMAC signature."""
        timestamp = int(time.time())
        signature = create_signature(method, path, timestamp, body, self.secret)
        
        return {
            'X-Key-Id': self.key_id,
            'X-Timestamp': str(timestamp),
            'X-Signature': signature,
            'Content-Type': 'application/json',
            'X-Correlation-Id': str(uuid.uuid4()),
        }
    
    def _handle_response(self, response: requests.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except:
            data = {}
        
        if response.status_code in [200, 201]:
            return data
        
        error_msg = data.get('error', {}).get('message', 'Unknown error')
        
        if response.status_code == 400:
            raise ValidationError(error_msg, status_code=400)
        elif response.status_code == 401:
            raise AuthenticationError(error_msg, status_code=401)
        elif response.status_code >= 500:
            raise ServerError(error_msg, status_code=response.status_code)
        else:
            raise CRLAPIError(error_msg, status_code=response.status_code)
    
    def calculate(self, mode: str, S0: float, ST: float, K: float, 
                  L: int, premium: float, side: str) -> CalcResponse:
        """
        Calculate CRL payoff.
        
        Example:
            >>> client = CRLClient(key_id="test", secret="secret")
            >>> result = client.calculate(
            ...     mode="crl", S0=100.0, ST=108.0, K=105.0,
            ...     L=5, premium=150.0, side="long"
            ... )
            >>> print(f"PnL: {result.pnl}, State: {result.state}")
        """
        # Validate with Pydantic
        request = CalcRequest(
            mode=mode, S0=S0, ST=ST, K=K, L=L, premium=premium, side=side
        )
        
        # Prepare request
        body = json.dumps(request.model_dump(exclude_none=True))
        headers = self._create_headers("POST", "/calc", body)
        url = urljoin(self.base_url, "/calc")
        
        # Make request
        response = self.session.post(url, headers=headers, data=body, timeout=30)
        
        # Handle response
        response_data = self._handle_response(response)
        return CalcResponse(**response_data)
