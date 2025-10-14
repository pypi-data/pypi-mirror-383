import requests
from adxp_sdk.auth.credentials import Credentials


class AXApiKeyHub:
    """SDK for managing API Keys."""

    def __init__(self, headers=None, base_url=None, credentials: Credentials = None):
        self.headers = headers
        self.base_url = base_url or (credentials.base_url if credentials else None)
        self.credentials = credentials

    def _get_headers(self):
        if self.headers:
            return self.headers
        elif self.credentials:
            return self.credentials.get_headers()
        else:
            raise ValueError("No authentication provided")

    def list_apikeys(self, page=1, size=10, sort=None, filter=None, search=None):
        """List API Keys"""
        url = f"{self.base_url}/api/v1/apikeys"
        params = {
            "page": page,
            "size": size,
            "sort": sort,
            "filter": filter,
            "search": search,
        }
        params = {k: v for k, v in params.items() if v is not None}
        resp = requests.get(url, headers=self._get_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def create_apikey(self, data: dict):
        """Create API Key"""
        url = f"{self.base_url}/api/v1/apikeys"
        resp = requests.post(url, headers=self._get_headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    def update_apikey(self, api_key_id: str, data: dict):
        """Update API Key"""
        url = f"{self.base_url}/api/v1/apikeys/{api_key_id}"
        resp = requests.put(url, headers=self._get_headers(), json=data)
        resp.raise_for_status()
        return resp.json()
    
    def delete_apikey(self, api_key_id: str):
        """Delete API Key"""
        url = f"{self.base_url}/api/v1/apikeys/{api_key_id}"
        resp = requests.delete(url, headers=self._get_headers())
        resp.raise_for_status()
        return resp.json() if resp.text else {"message": "Deleted successfully"}

