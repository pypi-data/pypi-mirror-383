"""API client for OmnibusX SDK."""

import httpx


class ApiClient:
    """Client for interacting with the OmnibusX API."""

    def __init__(self, base_url: str, token: str, enable_https: bool = True) -> None:
        """Initialize the client with base URL and authentication token."""
        self.base_url = base_url
        self.token = token
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "OmnibusX-SDK/1.0",
            },
            verify=enable_https,
            timeout=30,
        )

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Send a GET request to the specified endpoint."""
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict | None = None) -> dict:
        """Send a POST request to the specified endpoint."""
        response = self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
