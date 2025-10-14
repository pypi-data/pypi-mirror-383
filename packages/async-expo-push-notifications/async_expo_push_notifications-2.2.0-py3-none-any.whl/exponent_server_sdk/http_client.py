"""
HTTP client protocols for dependency injection.
"""

from typing import Protocol, Optional, Dict, Any
import requests
import httpx


class HTTPClientProtocol(Protocol):
    """Protocol for HTTP clients that can be injected into PushClient."""

    def post(
        self,
        url: str,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        """Make a POST request."""
        ...


class AsyncHTTPClientProtocol(Protocol):
    """Protocol for async HTTP clients that can be injected into AsyncPushClient."""

    async def post(
        self,
        url: str,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Make an async POST request."""
        ...
