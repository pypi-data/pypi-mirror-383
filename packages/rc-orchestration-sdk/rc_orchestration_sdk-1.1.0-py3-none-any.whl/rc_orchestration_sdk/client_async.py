"""
Asynchronous client for FounderX-AI Orchestration API.

This module provides a production-quality async client with comprehensive error handling,
retry logic, pagination, and full API coverage using httpx.
"""

import asyncio
import logging
import os
from typing import Any, AsyncIterator, BinaryIO, Dict, Iterator, List, Optional, Union

import httpx

from .exceptions import (
    AuthenticationError,
    NetworkError,
    OrchestrationError,
    TimeoutError,
    handle_http_error,
)
from .models import (
    Artifact,
    ExecutionRequest,
    ExecutionResponse,
    LoginResponse,
    MarketplaceTemplate,
    PaginatedResponse,
    Settings,
    SystemStatus,
    UsageStats,
    WebhookConfig,
    WebhookCreateRequest,
)

logger = logging.getLogger(__name__)


class AsyncOrchestrationClient:
    """
    Asynchronous client for FounderX-AI Orchestration API.

    Supports authentication, execution management, artifacts, webhooks,
    marketplace, analytics, and settings with comprehensive error handling
    and automatic retries.

    Example:
        >>> async with AsyncOrchestrationClient(base_url="https://api.example.com") as client:
        ...     await client.login("username", "password")
        ...     execution = await client.execute(template_id="my-template")
        ...     artifacts = await client.list_artifacts(execution.execution_id)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        access_token: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the async orchestration client.

        Args:
            base_url: API base URL (default: ORCH_BASE_URL env var or http://localhost:8000/api/v1)
            access_token: Access token for authenticated requests (default: ORCH_ACCESS_TOKEN env var)
            api_key: API key for public API requests (default: PUBLIC_API_KEY env var)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.base_url = (base_url or os.getenv("ORCH_BASE_URL", "http://localhost:8000/api/v1")).rstrip("/")
        self.access_token = access_token or os.getenv("ORCH_ACCESS_TOKEN")
        self.api_key = api_key or os.getenv("PUBLIC_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries
        self.refresh_token: Optional[str] = None

        # Create async HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )

    def _get_headers(self, use_api_key: bool = False) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        use_api_key: bool = False,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Make async HTTP request with error handling and retries.

        Args:
            method: HTTP method
            endpoint: API endpoint
            use_api_key: Use API key instead of access token
            json: JSON request body
            data: Raw request body
            files: Files for multipart upload
            params: Query parameters

        Returns:
            Response object

        Raises:
            OrchestrationError: On API errors
            NetworkError: On network errors
            TimeoutError: On request timeout
        """
        headers = self._get_headers(use_api_key=use_api_key)
        if files:
            headers.pop("Content-Type", None)

        url = endpoint.lstrip("/")

        # Retry logic
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"{method} {url} (api_key={use_api_key}, attempt={attempt+1})")
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                )

                # Retry on rate limit or server errors
                if response.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    wait_time = (2**attempt) * 0.5  # Exponential backoff
                    logger.warning(f"Request failed with {response.status_code}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue

                # Handle errors
                if not response.is_success:
                    error_message = response.text
                    try:
                        error_data = response.json()
                        error_message = error_data.get("detail", error_message)
                    except Exception:
                        pass

                    logger.error(f"{method} {url} failed: {response.status_code} {error_message}")
                    raise handle_http_error(response.status_code, error_message, response=None)

                return response

            except httpx.TimeoutException as e:
                if attempt < self.max_retries:
                    wait_time = (2**attempt) * 0.5
                    logger.warning(f"Request timeout, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                logger.error(f"Request timeout: {e}")
                raise TimeoutError(f"Request timed out after {self.timeout}s") from e
            except httpx.ConnectError as e:
                if attempt < self.max_retries:
                    wait_time = (2**attempt) * 0.5
                    logger.warning(f"Connection error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                logger.error(f"Connection error: {e}")
                raise NetworkError(f"Connection failed: {e}") from e
            except OrchestrationError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise OrchestrationError(f"Unexpected error: {e}") from e

        raise OrchestrationError("Max retries exceeded")

    # ==================== Authentication ====================

    async def login(self, username: str, password: str) -> LoginResponse:
        """
        Authenticate and obtain access tokens.

        Args:
            username: Username
            password: Password

        Returns:
            Login response with tokens
        """
        response = await self._request("POST", "/auth/login", json={"username": username, "password": password})
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        logger.info(f"Logged in as {username}")
        return LoginResponse(**data)

    async def refresh_access_token(self) -> LoginResponse:
        """
        Refresh access token using refresh token.

        Returns:
            New tokens
        """
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")

        response = await self._request("POST", "/auth/refresh", json={"refresh_token": self.refresh_token})
        data = response.json()
        self.access_token = data["access_token"]
        logger.info("Access token refreshed")
        return LoginResponse(**data)

    async def logout(self) -> None:
        """Logout and clear tokens."""
        try:
            await self._request("POST", "/auth/logout")
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
        finally:
            self.access_token = None
            self.refresh_token = None
            logger.info("Logged out")

    # ==================== System Status ====================

    async def status(self, use_api_key: bool = False) -> SystemStatus:
        """Get system status."""
        response = await self._request("GET", "/status", use_api_key=use_api_key)
        return SystemStatus(**response.json())

    async def health(self) -> Dict[str, Any]:
        """Health check endpoint."""
        response = await self._request("GET", "/health")
        return response.json()

    # ==================== Orchestration Execution ====================

    async def execute(
        self,
        template_id: Optional[str] = None,
        template_yaml: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        workspace: str = "default",
        priority: int = 0,
        timeout: Optional[int] = None,
        tags: Optional[List[str]] = None,
        use_api_key: bool = False,
    ) -> ExecutionResponse:
        """Start orchestration execution."""
        request = ExecutionRequest(
            template_id=template_id,
            template_yaml=template_yaml,
            parameters=parameters or {},
            workspace=workspace,
            priority=priority,
            timeout=timeout,
            tags=tags or [],
        )
        response = await self._request("POST", "/orchestration/execute", use_api_key=use_api_key, json=request.__dict__)
        data = response.json()
        logger.info(f"Started execution {data['execution_id']}")
        return ExecutionResponse(**data)

    async def get_execution(self, execution_id: str, use_api_key: bool = False) -> ExecutionResponse:
        """Get execution status and results."""
        response = await self._request("GET", f"/orchestration/executions/{execution_id}", use_api_key=use_api_key)
        return ExecutionResponse(**response.json())

    async def list_executions(
        self,
        workspace: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        use_api_key: bool = False,
    ) -> PaginatedResponse:
        """List executions with filtering."""
        params = {"limit": limit, "offset": offset}
        if workspace:
            params["workspace"] = workspace
        if status:
            params["status"] = status

        response = await self._request("GET", "/orchestration/executions", use_api_key=use_api_key, params=params)
        data = response.json()
        return PaginatedResponse(
            items=[ExecutionResponse(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", limit),
            total_pages=data.get("total_pages", 1),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    async def cancel_execution(self, execution_id: str) -> ExecutionResponse:
        """Cancel running execution."""
        response = await self._request("POST", f"/orchestration/executions/{execution_id}/cancel")
        logger.info(f"Cancelled execution {execution_id}")
        return ExecutionResponse(**response.json())

    async def stream_execution(self, execution_id: str, use_api_key: bool = False) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream execution updates via SSE.

        Args:
            execution_id: Execution ID
            use_api_key: Use API key for public access

        Yields:
            Execution update events
        """
        headers = self._get_headers(use_api_key=use_api_key)
        url = f"/orchestration/executions/{execution_id}/stream"

        async with self.client.stream("GET", url, headers=headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json

                    yield json.loads(line[6:])

    # ==================== Artifacts ====================

    async def list_artifacts(
        self,
        execution_id: Optional[str] = None,
        workspace: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        use_api_key: bool = False,
    ) -> PaginatedResponse:
        """List artifacts with filtering."""
        params = {"limit": limit, "offset": offset}
        if execution_id:
            params["execution_id"] = execution_id
        if workspace:
            params["workspace"] = workspace

        response = await self._request("GET", "/artifacts", use_api_key=use_api_key, params=params)
        data = response.json()
        return PaginatedResponse(
            items=[Artifact(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", limit),
            total_pages=data.get("total_pages", 1),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    async def get_artifact(self, artifact_id: str, use_api_key: bool = False) -> Artifact:
        """Get artifact metadata."""
        response = await self._request("GET", f"/artifacts/{artifact_id}", use_api_key=use_api_key)
        return Artifact(**response.json())

    async def download_artifact(self, artifact_id: str, output_path: str, use_api_key: bool = False) -> None:
        """Download artifact content to file."""
        headers = self._get_headers(use_api_key=use_api_key)
        url = f"/artifacts/{artifact_id}/download"

        async with self.client.stream("GET", url, headers=headers) as response:
            with open(output_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)

        logger.info(f"Downloaded artifact {artifact_id} to {output_path}")

    async def download_artifact_content(self, artifact_id: str, use_api_key: bool = False) -> bytes:
        """Download artifact content as bytes."""
        response = await self._request("GET", f"/artifacts/{artifact_id}/download", use_api_key=use_api_key)
        return response.content

    async def sign_artifact(self, artifact_id: str, use_api_key: bool = False) -> Artifact:
        """Sign artifact with GPG."""
        response = await self._request("POST", f"/artifacts/{artifact_id}/sign", use_api_key=use_api_key)
        logger.info(f"Signed artifact {artifact_id}")
        return Artifact(**response.json())

    # ==================== Webhooks ====================

    async def list_webhooks(self, use_api_key: bool = False) -> List[WebhookConfig]:
        """List registered webhooks."""
        response = await self._request("GET", "/webhooks", use_api_key=use_api_key)
        return [WebhookConfig(**item) for item in response.json()]

    async def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_api_key: bool = False,
    ) -> WebhookConfig:
        """Register new webhook."""
        request = WebhookCreateRequest(url=url, events=events, secret=secret, metadata=metadata or {})
        response = await self._request("POST", "/webhooks", use_api_key=use_api_key, json=request.__dict__)
        logger.info(f"Created webhook for {url}")
        return WebhookConfig(**response.json())

    async def delete_webhook(self, webhook_id: str, use_api_key: bool = False) -> None:
        """Delete webhook."""
        await self._request("DELETE", f"/webhooks/{webhook_id}", use_api_key=use_api_key)
        logger.info(f"Deleted webhook {webhook_id}")

    # ==================== Marketplace ====================

    async def list_marketplace_templates(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> PaginatedResponse:
        """List marketplace templates."""
        params = {"limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if search:
            params["search"] = search

        response = await self._request("GET", "/marketplace/templates", params=params)
        data = response.json()
        return PaginatedResponse(
            items=[MarketplaceTemplate(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", limit),
            total_pages=data.get("total_pages", 1),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    async def get_marketplace_template(self, template_id: str) -> MarketplaceTemplate:
        """Get marketplace template details."""
        response = await self._request("GET", f"/marketplace/templates/{template_id}")
        return MarketplaceTemplate(**response.json())

    # ==================== Analytics ====================

    async def get_usage_stats(
        self,
        workspace: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> UsageStats:
        """Get usage statistics."""
        params = {}
        if workspace:
            params["workspace"] = workspace
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._request("GET", "/analytics/usage", params=params)
        return UsageStats(**response.json())

    # ==================== Settings ====================

    async def get_settings(self, workspace: str = "default") -> Settings:
        """Get workspace settings."""
        response = await self._request("GET", f"/settings/{workspace}")
        return Settings(**response.json())

    async def update_settings(self, workspace: str = "default", settings: Dict[str, Any] = None) -> Settings:
        """Update workspace settings."""
        response = await self._request("PUT", f"/settings/{workspace}", json=settings or {})
        logger.info(f"Updated settings for workspace {workspace}")
        return Settings(**response.json())

    # ==================== Pagination Helpers ====================

    async def iter_all_executions(
        self,
        workspace: Optional[str] = None,
        status: Optional[str] = None,
        page_size: int = 50,
        use_api_key: bool = False,
    ) -> AsyncIterator[ExecutionResponse]:
        """Iterate over all executions with automatic pagination."""
        offset = 0
        while True:
            page = await self.list_executions(workspace=workspace, status=status, limit=page_size, offset=offset, use_api_key=use_api_key)
            for item in page.items:
                yield item
            if not page.has_next:
                break
            offset += page_size

    async def iter_all_artifacts(
        self,
        execution_id: Optional[str] = None,
        workspace: Optional[str] = None,
        page_size: int = 50,
        use_api_key: bool = False,
    ) -> AsyncIterator[Artifact]:
        """Iterate over all artifacts with automatic pagination."""
        offset = 0
        while True:
            page = await self.list_artifacts(execution_id=execution_id, workspace=workspace, limit=page_size, offset=offset, use_api_key=use_api_key)
            for item in page.items:
                yield item
            if not page.has_next:
                break
            offset += page_size

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close client."""
        await self.client.aclose()
