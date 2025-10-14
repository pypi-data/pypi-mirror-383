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

__version__ = "1.0.0"
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
]