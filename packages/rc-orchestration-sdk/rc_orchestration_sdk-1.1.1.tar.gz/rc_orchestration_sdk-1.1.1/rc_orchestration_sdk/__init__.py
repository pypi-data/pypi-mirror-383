"""
FounderX-AI Orchestration SDK for Python.

This SDK provides both synchronous and asynchronous clients for the FounderX-AI Orchestration API,
with comprehensive error handling, retry logic, pagination, and full API coverage.

Example (Sync):
    >>> from rc_orchestration_sdk import OrchestrationClient
    >>> client = OrchestrationClient(base_url="https://api.example.com")
    >>> client.login("username", "password")
    >>> execution = client.execute(template_id="my-template")

Example (Async):
    >>> from rc_orchestration_sdk import AsyncOrchestrationClient
    >>> async with AsyncOrchestrationClient(base_url="https://api.example.com") as client:
    ...     await client.login("username", "password")
    ...     execution = await client.execute(template_id="my-template")
"""

from .client import OrchestrationClient as LegacyOrchestrationClient
from .client_async import AsyncOrchestrationClient
from .client_sync import OrchestrationClient
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    OrchestrationError,
    RateLimitError,
    ServerError,
    StreamError,
    TimeoutError,
    ValidationError,
)
from .models import (
    Artifact,
    ArtifactType,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatus,
    LoginRequest,
    LoginResponse,
    MarketplaceTemplate,
    PaginatedResponse,
    Settings,
    SystemStatus,
    UsageStats,
    WebhookConfig,
    WebhookCreateRequest,
    WebhookEvent,
)

__version__ = "1.1.1"

__all__ = [
    # Clients
    "OrchestrationClient",
    "AsyncOrchestrationClient",
    "LegacyOrchestrationClient",
    # Exceptions
    "OrchestrationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    "StreamError",
    # Models
    "ExecutionRequest",
    "ExecutionResponse",
    "ExecutionStatus",
    "LoginRequest",
    "LoginResponse",
    "Artifact",
    "ArtifactType",
    "WebhookConfig",
    "WebhookCreateRequest",
    "WebhookEvent",
    "SystemStatus",
    "UsageStats",
    "MarketplaceTemplate",
    "Settings",
    "PaginatedResponse",
]
