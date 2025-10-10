"""
Data models for the FounderX-AI Orchestration SDK.

This module defines typed models for API requests and responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ArtifactType(str, Enum):
    """Artifact type enumeration."""
    FILE = "file"
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"


class WebhookEvent(str, Enum):
    """Webhook event types."""
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    ARTIFACT_CREATED = "artifact.created"


@dataclass
class LoginRequest:
    """Login request data."""
    username: str
    password: str


@dataclass
class LoginResponse:
    """Login response data."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


@dataclass
class ExecutionRequest:
    """Orchestration execution request."""
    template_id: Optional[str] = None
    template_yaml: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    workspace: str = "default"
    priority: int = 0
    timeout: Optional[int] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ExecutionResponse:
    """Orchestration execution response."""
    execution_id: str
    status: ExecutionStatus
    workspace: str
    created_at: str
    updated_at: str
    template_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    artifacts: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)


@dataclass
class Artifact:
    """Artifact metadata."""
    artifact_id: str
    execution_id: str
    name: str
    type: ArtifactType
    size: int
    created_at: str
    workspace: str
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    version: Optional[str] = None
    signed: bool = False
    signature: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class WebhookConfig:
    """Webhook configuration."""
    webhook_id: str
    url: str
    events: List[WebhookEvent]
    secret: str
    active: bool = True
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookCreateRequest:
    """Webhook creation request."""
    url: str
    events: List[str]
    secret: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemStatus:
    """System status response."""
    status: str
    version: str
    uptime: float
    active_executions: int
    queued_executions: int
    total_executions: int
    providers: Dict[str, str] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Usage statistics."""
    workspace: str
    period: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_duration: float
    total_tokens: int
    total_cost: float
    provider_breakdown: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketplaceTemplate:
    """Marketplace template."""
    template_id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    rating: float
    downloads: int
    created_at: str
    updated_at: str
    tags: List[str] = field(default_factory=list)
    yaml_content: Optional[str] = None
    readme: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Settings:
    """User/workspace settings."""
    workspace: str
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    rate_limits: Dict[str, int] = field(default_factory=dict)
    quotas: Dict[str, int] = field(default_factory=dict)
    notifications: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaginatedResponse:
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
