"""OmnibusX SDK for Python."""

import json
import time
from pathlib import Path

import httpx

from .api_client import ApiClient
from .models import (
    AddTaskParams,
    AddTaskResponse,
    ImportOmnibusXFileParams,
    TaskLog,
    TaskStatus,
    TaskType,
    UserGroup,
)

AUTH0_DOMAIN = "omnibusx.us.auth0.com"
CLIENT_ID = "695G9N2XeZRjme75lAbjqC80yq28cpUn"
API_AUDIENCE = "https://api-prod.omnibusx.com"
SCOPES = "openid profile email"


class SDKClient:
    """Base class for OmnibusX SDK client."""

    def __init__(self, server_url: str, enable_https: bool = True) -> None:
        """Initialize the SDK client with base URL and authentication token."""
        self._server_url = server_url
        self._enable_https = enable_https
        self._access_token = None
        self._cache_path = Path.cwd().joinpath(".omnibusx_token_cache.json")
        self._client = None

    def _start_device_authorization(self) -> None:
        """Request a device code from Auth0 for user authentication."""
        url = f"https://{AUTH0_DOMAIN}/oauth/device/code"
        payload = {
            "client_id": CLIENT_ID,
            "scope": SCOPES,
            "audience": API_AUDIENCE,
        }
        try:
            response = httpx.post(url, data=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error starting device authorization: {e}")
            return None

    def _poll_for_token(self, device_code_info: dict) -> dict | None:
        """Poll the token endpoint until the user completes authentication."""
        url = f"https://{AUTH0_DOMAIN}/oauth/token"
        payload = {
            "client_id": CLIENT_ID,
            "device_code": device_code_info["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        interval = device_code_info.get("interval", 5)
        print("Please complete the authentication in your browser.")
        while True:
            time.sleep(interval)
            try:
                response = httpx.post(url, data=payload)
                data = response.json()

                if response.status_code == 200:
                    print("Authentication successful.")
                    return data
                if data.get("error") == "authorization_pending":
                    print(".", end="", flush=True)
                    continue
                if data.get("error") == "slow_down":
                    interval += 5
                    print(f"Slowing down polling to {interval} seconds.")
                    continue
                print(
                    f"Error during authentication: {data.get('error_description', 'Unknown error')}"
                )
            except httpx.HTTPStatusError as e:
                print(f"HTTP error during token polling: {e}")
                return None
            else:
                return None

    def _load_token_from_cache(self) -> bool:
        """Load the access token from cache if it exists."""
        if self._cache_path.exists():
            try:
                with open(self._cache_path, "r") as file:
                    cached_data = json.load(file)
                    # Check if token is expired
                    if cached_data.get("expires_at", 0) > time.time() + 60:
                        self._access_token = cached_data.get("access_token")
                        return True
            except Exception as e:
                print(f"Error reading token cache: {e}")
        return False

    def _save_token_to_cache(self, token_data: dict) -> None:
        expires_at = token_data.get("expires_in", 0) + int(time.time())
        cache_content = {
            "access_token": token_data.get("access_token"),
            "expires_at": expires_at,
        }
        with open(self._cache_path, "w") as file:
            json.dump(cache_content, file)

    def authenticate(self, cache_token: bool = True) -> bool:
        if cache_token and self._load_token_from_cache():
            self._client = ApiClient(
                base_url=self._server_url,
                token=self._access_token,
                enable_https=self._enable_https,
            )
            return True

        device_code_data = self._start_device_authorization()
        if not device_code_data:
            return False

        print("=== ACTION REQUIRED ===")
        print(
            f"1. Open this URL in your browser: {device_code_data['verification_uri_complete']}"
        )
        print(
            f"2. Make sure the code displayed in the browser matches: {device_code_data['user_code']}"
        )
        print("3. Follow the instructions to complete authentication.")

        token_data = self._poll_for_token(device_code_data)
        if token_data and "access_token" in token_data:
            self._access_token = token_data["access_token"]
            self._client = ApiClient(
                base_url=self._server_url,
                token=self._access_token,
                enable_https=self._enable_https,
            )
            if cache_token:
                self._save_token_to_cache(token_data)
            return True
        return False

    def clear_token_cache(self) -> None:
        """Clear the cached access token."""
        if self._cache_path.exists():
            try:
                self._cache_path.unlink()
                print("Token cache cleared.")
            except Exception as e:
                print(f"Error clearing token cache: {e}")
        else:
            print("No token cache found to clear.")

    def _add_task(self, task_params: AddTaskParams) -> AddTaskResponse:
        """Add a new task to the OmnibusX API."""
        response = self._client.post("/api/tasks/add", data=task_params.model_dump())
        return AddTaskResponse(**response)

    def _commit_task(self, task_id: str) -> None:
        """Comnit a task by its ID."""
        self._client.post("/api/tasks/commit-result", data={"task_id": task_id})

    def _get_task(self, task_id: str) -> TaskLog:
        """Get detailed information about a specific task."""
        response = self._client.get("/api/tasks/get", params={"task_id": task_id})
        return TaskLog(**response)

    def test_connection(self) -> bool:
        """Test the connection to the OmnibusX API."""
        try:
            response = self._client.get("/health-check")
            if response.get("status") != "ok":
                raise ValueError(response.get("message", "Connection failed"))
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
        else:
            print("Connection successful")
            return True

    def get_available_groups(self) -> list[UserGroup]:
        """Get a list of available user groups."""
        response = self._client.get("/api/user-groups/get")
        return [
            UserGroup(
                user_group_id=group["id"],
                name=group["name"],
                description=group["description"],
            )
            for group in response
        ]

    def import_omnibusx_file(self, omnibusx_file_path: str, group_id: str) -> str:
        """Import an OmnibusX file."""
        params = ImportOmnibusXFileParams(
            omnibusx_file_path=omnibusx_file_path, group_id=group_id
        )
        task_params = AddTaskParams(
            task_type=TaskType.IMPORT_OMNIBUSX_FILE, params=params
        )
        add_task_response = self._add_task(task_params)
        return add_task_response.task_id

    def preprocess_dataset(self, params: dict, group_id: str) -> str:
        """Preprocess a dataset."""
        params["group_id"] = group_id
        task_params = AddTaskParams(
            task_type=TaskType.PREPROCESS_DATASET, params=params
        )
        add_task_response = self._add_task(task_params)
        return add_task_response.task_id

    def get_task_info(self, task_id: str, interval: int = 5) -> TaskLog:
        """Get information about a specific task."""
        while True:
            task_info = self._get_task(task_id)
            print(task_info.log, end="\r", flush=True)
            if task_info.status not in (TaskStatus.SUCCESS, TaskStatus.FAILED):
                time.sleep(interval)
            elif task_info.status == TaskStatus.SUCCESS and not task_info.is_committed:
                self._commit_task(task_id)
                break
            else:
                break
