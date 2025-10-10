"""
Synchronous client for FounderX-AI Orchestration API.

This module provides a production-quality sync client with comprehensive error handling,
retry logic, pagination, and full API coverage.
"""

import logging
import os
import time
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter, Retry

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
    LoginRequest,
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


class OrchestrationClient:
    """
    Synchronous client for FounderX-AI Orchestration API.

    Supports authentication, execution management, artifacts, webhooks,
    marketplace, analytics, and settings with comprehensive error handling
    and automatic retries.

    Example:
        >>> client = OrchestrationClient(base_url="https://api.example.com")
        >>> client.login("username", "password")
        >>> execution = client.execute(template_id="my-template")
        >>> artifacts = client.list_artifacts(execution.execution_id)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        access_token: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize the orchestration client.

        Args:
            base_url: API base URL (default: ORCH_BASE_URL env var or http://localhost:8000/api/v1)
            access_token: Access token for authenticated requests (default: ORCH_ACCESS_TOKEN env var)
            api_key: API key for public API requests (default: PUBLIC_API_KEY env var)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
            backoff_factor: Backoff factor for retries (default: 0.5)
        """
        self.base_url = (base_url or os.getenv("ORCH_BASE_URL", "http://localhost:8000/api/v1")).rstrip("/")
        self.access_token = access_token or os.getenv("ORCH_ACCESS_TOKEN")
        self.api_key = api_key or os.getenv("PUBLIC_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.refresh_token: Optional[str] = None

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            backoff_factor=backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_headers(self, use_api_key: bool = False) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if use_api_key and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        use_api_key: bool = False,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> requests.Response:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint (will be joined with base_url)
            use_api_key: Use API key instead of access token
            json: JSON request body
            data: Raw request body
            files: Files for multipart upload
            params: Query parameters
            stream: Enable streaming response

        Returns:
            Response object

        Raises:
            OrchestrationError: On API errors
            NetworkError: On network errors
            TimeoutError: On request timeout
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        headers = self._get_headers(use_api_key=use_api_key)

        # Remove Content-Type for file uploads
        if files:
            headers.pop("Content-Type", None)

        try:
            logger.debug(f"{method} {url} (api_key={use_api_key})")
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                data=data,
                files=files,
                params=params,
                timeout=self.timeout,
                stream=stream,
            )

            # Handle errors
            if not response.ok:
                error_message = response.text
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail", error_message)
                except Exception:
                    pass

                logger.error(f"{method} {url} failed: {response.status_code} {error_message}")
                raise handle_http_error(response.status_code, error_message, response=None)

            return response

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request timed out after {self.timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"Connection failed: {e}") from e
        except OrchestrationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise OrchestrationError(f"Unexpected error: {e}") from e

    # ==================== Authentication ====================

    def login(self, username: str, password: str) -> LoginResponse:
        """
        Authenticate and obtain access tokens.

        Args:
            username: Username
            password: Password

        Returns:
            Login response with tokens

        Raises:
            AuthenticationError: If login fails
        """
        response = self._request("POST", "/auth/login", json={"username": username, "password": password})
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        logger.info(f"Logged in as {username}")
        return LoginResponse(**data)

    def refresh_access_token(self) -> LoginResponse:
        """
        Refresh access token using refresh token.

        Returns:
            New tokens

        Raises:
            AuthenticationError: If refresh fails
        """
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")

        response = self._request("POST", "/auth/refresh", json={"refresh_token": self.refresh_token})
        data = response.json()
        self.access_token = data["access_token"]
        logger.info("Access token refreshed")
        return LoginResponse(**data)

    def logout(self) -> None:
        """Logout and clear tokens."""
        try:
            self._request("POST", "/auth/logout")
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
        finally:
            self.access_token = None
            self.refresh_token = None
            logger.info("Logged out")

    # ==================== System Status ====================

    def status(self, use_api_key: bool = False) -> SystemStatus:
        """
        Get system status.

        Args:
            use_api_key: Use API key for public access

        Returns:
            System status
        """
        response = self._request("GET", "/status", use_api_key=use_api_key)
        return SystemStatus(**response.json())

    def health(self) -> Dict[str, Any]:
        """
        Health check endpoint.

        Returns:
            Health status
        """
        response = self._request("GET", "/health")
        return response.json()

    # ==================== Orchestration Execution ====================

    def execute(
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
        """
        Start orchestration execution.

        Args:
            template_id: Template ID (if using saved template)
            template_yaml: Template YAML content (if using inline template)
            parameters: Execution parameters
            workspace: Workspace name
            priority: Execution priority (higher = more priority)
            timeout: Execution timeout in seconds
            tags: Tags for execution
            use_api_key: Use API key for public access

        Returns:
            Execution response

        Raises:
            ValidationError: If request validation fails
        """
        request = ExecutionRequest(
            template_id=template_id,
            template_yaml=template_yaml,
            parameters=parameters or {},
            workspace=workspace,
            priority=priority,
            timeout=timeout,
            tags=tags or [],
        )
        response = self._request("POST", "/orchestration/execute", use_api_key=use_api_key, json=request.__dict__)
        data = response.json()
        logger.info(f"Started execution {data['execution_id']}")
        return ExecutionResponse(**data)

    def get_execution(self, execution_id: str, use_api_key: bool = False) -> ExecutionResponse:
        """
        Get execution status and results.

        Args:
            execution_id: Execution ID
            use_api_key: Use API key for public access

        Returns:
            Execution response
        """
        response = self._request("GET", f"/orchestration/executions/{execution_id}", use_api_key=use_api_key)
        return ExecutionResponse(**response.json())

    def list_executions(
        self,
        workspace: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        use_api_key: bool = False,
    ) -> PaginatedResponse:
        """
        List executions with filtering.

        Args:
            workspace: Filter by workspace
            status: Filter by status
            limit: Maximum results per page
            offset: Offset for pagination
            use_api_key: Use API key for public access

        Returns:
            Paginated executions
        """
        params = {"limit": limit, "offset": offset}
        if workspace:
            params["workspace"] = workspace
        if status:
            params["status"] = status

        response = self._request("GET", "/orchestration/executions", use_api_key=use_api_key, params=params)
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

    def cancel_execution(self, execution_id: str) -> ExecutionResponse:
        """
        Cancel running execution.

        Args:
            execution_id: Execution ID

        Returns:
            Updated execution response
        """
        response = self._request("POST", f"/orchestration/executions/{execution_id}/cancel")
        logger.info(f"Cancelled execution {execution_id}")
        return ExecutionResponse(**response.json())

    def stream_execution(self, execution_id: str, use_api_key: bool = False) -> Iterator[Dict[str, Any]]:
        """
        Stream execution updates via SSE.

        Args:
            execution_id: Execution ID
            use_api_key: Use API key for public access

        Yields:
            Execution update events

        Raises:
            StreamError: If streaming fails
        """
        response = self._request("GET", f"/orchestration/executions/{execution_id}/stream", use_api_key=use_api_key, stream=True)

        try:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        import json

                        yield json.loads(decoded[6:])
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            from .exceptions import StreamError

            raise StreamError(f"Streaming failed: {e}") from e

    # ==================== Artifacts ====================

    def list_artifacts(
        self,
        execution_id: Optional[str] = None,
        workspace: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        use_api_key: bool = False,
    ) -> PaginatedResponse:
        """
        List artifacts with filtering.

        Args:
            execution_id: Filter by execution ID
            workspace: Filter by workspace
            limit: Maximum results per page
            offset: Offset for pagination
            use_api_key: Use API key for public access

        Returns:
            Paginated artifacts
        """
        params = {"limit": limit, "offset": offset}
        if execution_id:
            params["execution_id"] = execution_id
        if workspace:
            params["workspace"] = workspace

        response = self._request("GET", "/artifacts", use_api_key=use_api_key, params=params)
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

    def get_artifact(self, artifact_id: str, use_api_key: bool = False) -> Artifact:
        """
        Get artifact metadata.

        Args:
            artifact_id: Artifact ID
            use_api_key: Use API key for public access

        Returns:
            Artifact metadata
        """
        response = self._request("GET", f"/artifacts/{artifact_id}", use_api_key=use_api_key)
        return Artifact(**response.json())

    def download_artifact(self, artifact_id: str, output_path: str, use_api_key: bool = False) -> None:
        """
        Download artifact content to file.

        Args:
            artifact_id: Artifact ID
            output_path: Output file path
            use_api_key: Use API key for public access
        """
        response = self._request("GET", f"/artifacts/{artifact_id}/download", use_api_key=use_api_key, stream=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded artifact {artifact_id} to {output_path}")

    def download_artifact_content(self, artifact_id: str, use_api_key: bool = False) -> bytes:
        """
        Download artifact content as bytes.

        Args:
            artifact_id: Artifact ID
            use_api_key: Use API key for public access

        Returns:
            Artifact content bytes
        """
        response = self._request("GET", f"/artifacts/{artifact_id}/download", use_api_key=use_api_key)
        return response.content

    def upload_artifact(
        self,
        execution_id: str,
        name: str,
        file: Union[str, BinaryIO],
        artifact_type: str = "file",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """
        Upload artifact for execution.

        Args:
            execution_id: Execution ID
            name: Artifact name
            file: File path or file-like object
            artifact_type: Artifact type
            metadata: Artifact metadata

        Returns:
            Created artifact
        """
        if isinstance(file, str):
            with open(file, "rb") as f:
                return self._upload_artifact_file(execution_id, name, f, artifact_type, metadata)
        else:
            return self._upload_artifact_file(execution_id, name, file, artifact_type, metadata)

    def _upload_artifact_file(
        self,
        execution_id: str,
        name: str,
        file: BinaryIO,
        artifact_type: str,
        metadata: Optional[Dict[str, Any]],
    ) -> Artifact:
        """Internal method to upload artifact file."""
        files = {"file": (name, file)}
        data = {"execution_id": execution_id, "name": name, "type": artifact_type}
        if metadata:
            import json

            data["metadata"] = json.dumps(metadata)

        response = self._request("POST", "/artifacts/upload", files=files, data=data)
        logger.info(f"Uploaded artifact {name} for execution {execution_id}")
        return Artifact(**response.json())

    def sign_artifact(self, artifact_id: str, use_api_key: bool = False) -> Artifact:
        """
        Sign artifact with GPG.

        Args:
            artifact_id: Artifact ID
            use_api_key: Use API key for public access

        Returns:
            Updated artifact with signature
        """
        response = self._request("POST", f"/artifacts/{artifact_id}/sign", use_api_key=use_api_key)
        logger.info(f"Signed artifact {artifact_id}")
        return Artifact(**response.json())

    # ==================== Webhooks ====================

    def list_webhooks(self, use_api_key: bool = False) -> List[WebhookConfig]:
        """
        List registered webhooks.

        Args:
            use_api_key: Use API key for public access

        Returns:
            List of webhooks
        """
        response = self._request("GET", "/webhooks", use_api_key=use_api_key)
        return [WebhookConfig(**item) for item in response.json()]

    def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        use_api_key: bool = False,
    ) -> WebhookConfig:
        """
        Register new webhook.

        Args:
            url: Webhook URL
            events: List of events to subscribe to
            secret: Webhook secret for HMAC signing
            metadata: Additional metadata
            use_api_key: Use API key for public access

        Returns:
            Created webhook
        """
        request = WebhookCreateRequest(url=url, events=events, secret=secret, metadata=metadata or {})
        response = self._request("POST", "/webhooks", use_api_key=use_api_key, json=request.__dict__)
        logger.info(f"Created webhook for {url}")
        return WebhookConfig(**response.json())

    def delete_webhook(self, webhook_id: str, use_api_key: bool = False) -> None:
        """
        Delete webhook.

        Args:
            webhook_id: Webhook ID
            use_api_key: Use API key for public access
        """
        self._request("DELETE", f"/webhooks/{webhook_id}", use_api_key=use_api_key)
        logger.info(f"Deleted webhook {webhook_id}")

    def rotate_webhook_secret(self, webhook_id: str) -> WebhookConfig:
        """
        Rotate webhook HMAC secret.

        Args:
            webhook_id: Webhook ID

        Returns:
            Updated webhook with new secret
        """
        response = self._request("POST", f"/webhooks/{webhook_id}/rotate-secret")
        logger.info(f"Rotated secret for webhook {webhook_id}")
        return WebhookConfig(**response.json())

    # ==================== Marketplace ====================

    def list_marketplace_templates(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> PaginatedResponse:
        """
        List marketplace templates.

        Args:
            category: Filter by category
            search: Search query
            limit: Maximum results per page
            offset: Offset for pagination

        Returns:
            Paginated templates
        """
        params = {"limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if search:
            params["search"] = search

        response = self._request("GET", "/marketplace/templates", params=params)
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

    def get_marketplace_template(self, template_id: str) -> MarketplaceTemplate:
        """
        Get marketplace template details.

        Args:
            template_id: Template ID

        Returns:
            Template details
        """
        response = self._request("GET", f"/marketplace/templates/{template_id}")
        return MarketplaceTemplate(**response.json())

    # ==================== Analytics ====================

    def get_usage_stats(
        self,
        workspace: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> UsageStats:
        """
        Get usage statistics.

        Args:
            workspace: Workspace filter
            start_date: Start date (ISO format)
            end_date: End date (ISO format)

        Returns:
            Usage statistics
        """
        params = {}
        if workspace:
            params["workspace"] = workspace
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = self._request("GET", "/analytics/usage", params=params)
        return UsageStats(**response.json())

    # ==================== Settings ====================

    def get_settings(self, workspace: str = "default") -> Settings:
        """
        Get workspace settings.

        Args:
            workspace: Workspace name

        Returns:
            Settings
        """
        response = self._request("GET", f"/settings/{workspace}")
        return Settings(**response.json())

    def update_settings(self, workspace: str = "default", settings: Dict[str, Any] = None) -> Settings:
        """
        Update workspace settings.

        Args:
            workspace: Workspace name
            settings: Settings to update

        Returns:
            Updated settings
        """
        response = self._request("PUT", f"/settings/{workspace}", json=settings or {})
        logger.info(f"Updated settings for workspace {workspace}")
        return Settings(**response.json())

    # ==================== Pagination Helpers ====================

    def iter_all_executions(
        self,
        workspace: Optional[str] = None,
        status: Optional[str] = None,
        page_size: int = 50,
        use_api_key: bool = False,
    ) -> Iterator[ExecutionResponse]:
        """
        Iterate over all executions with automatic pagination.

        Args:
            workspace: Filter by workspace
            status: Filter by status
            page_size: Results per page
            use_api_key: Use API key for public access

        Yields:
            Execution responses
        """
        offset = 0
        while True:
            page = self.list_executions(workspace=workspace, status=status, limit=page_size, offset=offset, use_api_key=use_api_key)
            for item in page.items:
                yield item
            if not page.has_next:
                break
            offset += page_size

    def iter_all_artifacts(
        self,
        execution_id: Optional[str] = None,
        workspace: Optional[str] = None,
        page_size: int = 50,
        use_api_key: bool = False,
    ) -> Iterator[Artifact]:
        """
        Iterate over all artifacts with automatic pagination.

        Args:
            execution_id: Filter by execution ID
            workspace: Filter by workspace
            page_size: Results per page
            use_api_key: Use API key for public access

        Yields:
            Artifacts
        """
        offset = 0
        while True:
            page = self.list_artifacts(execution_id=execution_id, workspace=workspace, limit=page_size, offset=offset, use_api_key=use_api_key)
            for item in page.items:
                yield item
            if not page.has_next:
                break
            offset += page_size

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()
