# FounderX-AI Orchestration SDK for Python

[![PyPI version](https://badge.fury.io/py/rc-orchestration-sdk.svg)](https://pypi.org/project/rc-orchestration-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/rc-orchestration-sdk.svg)](https://pypi.org/project/rc-orchestration-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-quality Python SDK for the FounderX-AI Orchestration API with both synchronous and asynchronous support.

## Features

- **Sync & Async Support**: Use `OrchestrationClient` for sync or `AsyncOrchestrationClient` for async
- **Comprehensive Error Handling**: Custom exceptions for every error type
- **Automatic Retries**: Exponential backoff for rate limits and server errors
- **Type Hints**: Full type annotations throughout
- **Pagination Helpers**: Automatic pagination with iterator support
- **Streaming**: Real-time execution streaming via SSE
- **Full API Coverage**: All endpoints including auth, execution, artifacts, webhooks, marketplace, analytics, settings
- **Context Managers**: Proper resource cleanup with `with` statements

## Installation

```bash
pip install rc-orchestration-sdk
```

## Quick Start

### Synchronous Client

```python
from rc_orchestration_sdk import OrchestrationClient

# Initialize client
client = OrchestrationClient(base_url="https://api.example.com")

# Login
client.login("username", "password")

# Start execution
execution = client.execute(
    template_id="my-template",
    parameters={"env": "production"},
    workspace="default"
)

print(f"Execution started: {execution.execution_id}")

# List artifacts
artifacts = client.list_artifacts(execution_id=execution.execution_id)
for artifact in artifacts.items:
    print(f"Artifact: {artifact.name} ({artifact.size} bytes)")

# Download artifact
client.download_artifact(
    artifact_id="artifact-123",
    output_path="/tmp/result.json"
)
```

### Asynchronous Client

```python
import asyncio
from rc_orchestration_sdk import AsyncOrchestrationClient

async def main():
    # Use context manager for automatic cleanup
    async with AsyncOrchestrationClient(base_url="https://api.example.com") as client:
        # Login
        await client.login("username", "password")

        # Start execution
        execution = await client.execute(
            template_id="my-template",
            parameters={"env": "production"}
        )

        # Stream execution updates in real-time
        async for event in client.stream_execution(execution.execution_id):
            print(f"Event: {event['type']} - {event['data']}")

        # Iterate over all artifacts with automatic pagination
        async for artifact in client.iter_all_artifacts(execution_id=execution.execution_id):
            print(f"Artifact: {artifact.name}")

asyncio.run(main())
```

## Authentication

### Username/Password

```python
client = OrchestrationClient(base_url="https://api.example.com")
client.login("username", "password")
```

### Access Token

```python
client = OrchestrationClient(
    base_url="https://api.example.com",
    access_token="your-access-token"
)
```

### API Key (Public API)

```python
client = OrchestrationClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# Use api_key for public endpoints
status = client.status(use_api_key=True)
```

### Environment Variables

```bash
export ORCH_BASE_URL="https://api.example.com/api/v1"
export ORCH_ACCESS_TOKEN="your-access-token"
export PUBLIC_API_KEY="your-api-key"
```

```python
# Client automatically picks up environment variables
client = OrchestrationClient()
```

## Core Functionality

### Execution Management

```python
# Start execution
execution = client.execute(
    template_id="my-template",
    parameters={"key": "value"},
    workspace="default",
    priority=5,
    timeout=3600,
    tags=["production", "critical"]
)

# Get execution status
execution = client.get_execution("execution-123")
print(f"Status: {execution.status}")
print(f"Result: {execution.result}")

# List executions
executions = client.list_executions(
    workspace="default",
    status="completed",
    limit=50
)

# Cancel execution
client.cancel_execution("execution-123")

# Stream execution updates
for event in client.stream_execution("execution-123"):
    print(event)
```

### Artifact Management

```python
# List artifacts
artifacts = client.list_artifacts(
    execution_id="execution-123",
    workspace="default",
    limit=50
)

# Get artifact metadata
artifact = client.get_artifact("artifact-123")

# Download artifact to file
client.download_artifact("artifact-123", "/tmp/output.json")

# Download artifact to memory
content = client.download_artifact_content("artifact-123")

# Upload artifact
with open("/tmp/data.json", "rb") as f:
    artifact = client.upload_artifact(
        execution_id="execution-123",
        name="data.json",
        file=f,
        artifact_type="json",
        metadata={"version": "1.0"}
    )

# Sign artifact with GPG
signed_artifact = client.sign_artifact("artifact-123")
print(f"Signature: {signed_artifact.signature}")
```

### Webhooks

```python
# List webhooks
webhooks = client.list_webhooks()

# Create webhook
webhook = client.create_webhook(
    url="https://example.com/webhook",
    events=["execution.completed", "execution.failed"],
    secret="webhook-secret",
    metadata={"team": "engineering"}
)

# Delete webhook
client.delete_webhook("webhook-123")

# Rotate webhook secret
webhook = client.rotate_webhook_secret("webhook-123")
print(f"New secret: {webhook.secret}")
```

### Marketplace

```python
# List marketplace templates
templates = client.list_marketplace_templates(
    category="backend",
    search="rest api",
    limit=20
)

# Get template details
template = client.get_marketplace_template("template-123")
print(f"Name: {template.name}")
print(f"Rating: {template.rating}")
print(f"Downloads: {template.downloads}")
```

### Analytics & Settings

```python
# Get usage statistics
stats = client.get_usage_stats(
    workspace="default",
    start_date="2025-01-01",
    end_date="2025-01-31"
)
print(f"Total executions: {stats.total_executions}")
print(f"Total cost: ${stats.total_cost}")

# Get settings
settings = client.get_settings(workspace="default")

# Update settings
settings = client.update_settings(
    workspace="default",
    settings={
        "default_provider": "anthropic",
        "default_model": "claude-3-5-sonnet-20241022"
    }
)
```

## Advanced Features

### Automatic Pagination

```python
# Iterate over all executions automatically
for execution in client.iter_all_executions(workspace="default"):
    print(f"Execution: {execution.execution_id}")

# Iterate over all artifacts
for artifact in client.iter_all_artifacts(execution_id="execution-123"):
    print(f"Artifact: {artifact.name}")
```

### Context Manager

```python
# Automatic session cleanup
with OrchestrationClient(base_url="https://api.example.com") as client:
    client.login("username", "password")
    executions = client.list_executions()
    # Session automatically closed on exit
```

### Custom Configuration

```python
client = OrchestrationClient(
    base_url="https://api.example.com",
    timeout=60,              # Request timeout in seconds
    max_retries=5,           # Maximum retry attempts
    backoff_factor=1.0       # Exponential backoff factor
)
```

### Error Handling

```python
from rc_orchestration_sdk import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    NetworkError,
    TimeoutError
)

try:
    client.login("username", "wrong-password")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    print(f"Status code: {e.status_code}")

try:
    execution = client.execute(template_id="invalid")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Response: {e.response}")

try:
    artifact = client.get_artifact("nonexistent")
except NotFoundError as e:
    print(f"Not found: {e.message}")

try:
    # Too many requests
    for i in range(1000):
        client.status()
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
    print(f"Retry after: {e.retry_after} seconds")
```

## Requirements

- Python 3.9+
- requests >= 2.31.0
- httpx >= 0.25.0 (for async client)

## Version History

- **v1.0.0** (2025-01-10): Initial production release
  - Synchronous and asynchronous clients
  - Full API coverage
  - Comprehensive error handling
  - Automatic retries and pagination
  - Type hints throughout

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- Documentation: https://docs.founder-x.ai/orchestration/sdk/python
- Email: support@founder-x.ai

