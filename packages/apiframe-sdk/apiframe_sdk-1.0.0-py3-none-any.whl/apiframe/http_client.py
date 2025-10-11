"""
HTTP Client for Apiframe SDK
"""

import time
from typing import Any, Dict, Optional

import requests

from .exceptions import ApiframeError, AuthenticationError, RateLimitError, TimeoutError


class HttpClient:
    """HTTP client for making requests to Apiframe API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.apiframe.ai",
        timeout: int = 300,
    ) -> None:
        """
        Initialize HTTP client

        Args:
            api_key: Apiframe API key
            base_url: Base URL for API requests
            timeout: Request timeout in seconds (default: 300 = 5 minutes)
        """
        if not api_key:
            raise ApiframeError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _normalize_task_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize API response to match SDK types

        Args:
            data: Raw API response data

        Returns:
            Normalized response data
        """
        # Normalize task_id to id
        if "task_id" in data and "id" not in data:
            data["id"] = data["task_id"]

        # Normalize percentage (string) to progress (number)
        if "percentage" in data and "progress" not in data:
            percentage = data["percentage"]
            if isinstance(percentage, str):
                try:
                    data["progress"] = int(percentage)
                except ValueError:
                    data["progress"] = 0
            elif isinstance(percentage, (int, float)):
                data["progress"] = int(percentage)

        # Normalize status: API returns "finished" but SDK expects "completed"
        if data.get("status") == "finished":
            data["status"] = "completed"

        return data

    def _handle_error(self, response: requests.Response) -> None:
        """
        Handle HTTP error responses

        Args:
            response: HTTP response object

        Raises:
            ApiframeError: For API errors
            AuthenticationError: For 401 errors
            RateLimitError: For 429 errors
            TimeoutError: For 408 errors
        """
        try:
            data = response.json()
            message = data.get("message", response.text)
        except Exception:
            message = response.text

        status = response.status_code

        if status == 401:
            raise AuthenticationError(message)
        elif status == 429:
            raise RateLimitError(message)
        elif status == 408:
            raise TimeoutError(message)
        else:
            raise ApiframeError(
                message,
                code=data.get("code") if isinstance(data, dict) else None,
                status=status,
                details=data if isinstance(data, dict) else None,
            )

    def get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Make GET request

        Args:
            path: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dictionary

        Raises:
            ApiframeError: For API errors
            TimeoutError: For timeout errors
        """
        url = f"{self.base_url}{path}"

        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            data = response.json()

            # Normalize response
            if isinstance(data, dict):
                self._normalize_task_response(data)

                # Also normalize nested task objects (for fetch-many responses)
                if "tasks" in data and isinstance(data["tasks"], list):
                    data["tasks"] = [
                        self._normalize_task_response(task) for task in data["tasks"]
                    ]

            return data

        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout")
        except requests.exceptions.HTTPError:
            self._handle_error(response)
            raise  # This line won't be reached but satisfies type checkers
        except requests.exceptions.RequestException as e:
            raise ApiframeError(str(e))

    def post(
        self,
        path: str,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Make POST request

        Args:
            path: API endpoint path
            data: Request body data (will be JSON encoded unless files are provided)
            files: Files to upload (multipart/form-data)
            headers: Additional headers
            **kwargs: Additional arguments for requests

        Returns:
            Response data as dictionary

        Raises:
            ApiframeError: For API errors
            TimeoutError: For timeout errors
        """
        url = f"{self.base_url}{path}"

        # Prepare request
        request_kwargs: Dict[str, Any] = {"timeout": self.timeout, **kwargs}

        # Convert numeric index to string for Apiframe API
        if isinstance(data, dict) and "index" in data and isinstance(data["index"], int):
            data = data.copy()
            data["index"] = str(data["index"])

        # Handle multipart/form-data for file uploads
        if files:
            request_kwargs["files"] = files
            request_kwargs["data"] = data
            # Remove Content-Type header to let requests set it with boundary
            custom_headers = {k: v for k, v in self.session.headers.items() if k != "Content-Type"}
            if headers:
                custom_headers.update(headers)
            request_kwargs["headers"] = custom_headers
        else:
            request_kwargs["json"] = data
            if headers:
                request_kwargs["headers"] = {**self.session.headers, **headers}

        try:
            response = self.session.post(url, **request_kwargs)
            response.raise_for_status()
            data_response = response.json()

            # Normalize response
            if isinstance(data_response, dict):
                self._normalize_task_response(data_response)

                # Also normalize nested task objects (for fetch-many responses)
                if "tasks" in data_response and isinstance(data_response["tasks"], list):
                    data_response["tasks"] = [
                        self._normalize_task_response(task) for task in data_response["tasks"]
                    ]

            return data_response

        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout")
        except requests.exceptions.HTTPError:
            self._handle_error(response)
            raise  # This line won't be reached but satisfies type checkers
        except requests.exceptions.RequestException as e:
            raise ApiframeError(str(e))

    def close(self) -> None:
        """Close the HTTP session"""
        self.session.close()

    def __enter__(self) -> "HttpClient":
        """Context manager entry"""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit"""
        self.close()

