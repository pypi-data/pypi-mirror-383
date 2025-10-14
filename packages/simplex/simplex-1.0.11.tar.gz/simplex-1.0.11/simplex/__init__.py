"""
Simplex Python SDK

Official Python SDK for the Simplex API - A workflow automation platform.

Example usage:
    >>> from simplex import SimplexClient
    >>> client = SimplexClient(api_key="your-api-key")
    >>> result = client.workflows.run("workflow-id")
"""

from simplex.client import SimplexClient
from simplex.errors import (
    SimplexError,
    NetworkError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    WorkflowError,
)
from simplex.resources.workflow import Workflow
from simplex.resources.workflow_session import WorkflowSession
from simplex.webhook import (
    verify_simplex_webhook,
    verify_simplex_webhook_dict,
    WebhookVerificationError,
)

__version__ = "1.0.11"
__all__ = [
    "SimplexClient",
    "SimplexError",
    "NetworkError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "WorkflowError",
    "Workflow",
    "WorkflowSession",
    "verify_simplex_webhook",
    "verify_simplex_webhook_dict",
    "WebhookVerificationError",
]