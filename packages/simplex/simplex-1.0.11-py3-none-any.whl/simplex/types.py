"""
Type definitions for the Simplex SDK.

This module contains TypedDict classes and type aliases used throughout the SDK
for type hinting and documentation purposes.
"""

from typing import Any, Dict, List, Optional, TypedDict


class SimplexClientOptions(TypedDict, total=False):
    """
    Configuration options for the SimplexClient.
    
    Attributes:
        api_key: Your Simplex API key (required)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)
    """
    api_key: str
    timeout: int
    max_retries: int
    retry_delay: int


# Type alias for workflow variables
WorkflowVariables = Dict[str, Any]


class RunWorkflowRequest(TypedDict, total=False):
    """
    Request parameters for running a workflow.
    
    Attributes:
        workflow_id: The ID of the workflow to run (required)
        metadata: Optional metadata string to attach to the workflow run
        webhook_url: Optional webhook URL for status updates
        variables: Dictionary of variables to pass to the workflow
    """
    workflow_id: str
    metadata: str
    webhook_url: str
    variables: WorkflowVariables


class RunWorkflowResponse(TypedDict):
    """
    Response from running a workflow.
    
    Attributes:
        succeeded: Whether the workflow started successfully
        message: Human-readable status message
        session_id: Unique identifier for this workflow session
        vnc_url: URL for VNC access to the workflow session
    """
    succeeded: bool
    message: str
    session_id: str
    vnc_url: str


class WorkflowAction(TypedDict):
    """
    Represents a single action taken during workflow execution.
    
    Attributes:
        action: The type of action performed
        params: Parameters passed to the action
        result: Result returned by the action
        timestamp: ISO 8601 timestamp when the action occurred
    """
    action: str
    params: Any
    result: Any
    timestamp: str


class WorkflowStatusResponse(TypedDict):
    """
    Response from checking workflow status.
    
    Attributes:
        succeeded: Whether the status check succeeded
        completed: Whether the workflow has completed execution
        results: List of actions taken during workflow execution
        total_actions: Total number of actions performed
        session_id: The session ID being checked
        completed_at: ISO 8601 timestamp of completion (if completed)
    """
    succeeded: bool
    completed: bool
    results: List[WorkflowAction]
    total_actions: int
    session_id: str
    completed_at: Optional[str]


class CreateWorkflowSessionRequest(TypedDict, total=False):
    """
    Request parameters for creating a workflow session.
    
    Attributes:
        workflow_name: Name for the workflow (required)
        url: Starting URL for the workflow (required)
        proxies: Whether to use proxies (default: False)
        session_data: Optional JSON string of session data
    """
    workflow_name: str
    url: str
    proxies: bool
    session_data: str


class CreateWorkflowSessionResponse(TypedDict):
    """
    Response from creating a workflow session.
    
    Attributes:
        session_id: Unique identifier for the session
        workflow_id: ID of the created workflow
        livestream_url: URL to view the live browser session
        connect_url: URL to connect to the session
        vnc_url: URL for VNC access
    """
    session_id: str
    workflow_id: str
    livestream_url: str
    connect_url: str
    vnc_url: str


class AgenticRequest(TypedDict, total=False):
    """
    Request parameters for running an agentic task.
    
    Attributes:
        task: Natural language description of the task (required)
        session_id: Session to run the task in (required)
        max_steps: Maximum number of steps to take (optional)
        actions_to_exclude: List of action types to exclude (optional)
        variables: JSON string of variables for the task (optional)
    """
    task: str
    session_id: str
    max_steps: int
    actions_to_exclude: List[str]
    variables: str


class AgenticResponse(TypedDict):
    """
    Response from running an agentic task.
    
    Attributes:
        succeeded: Whether the task completed successfully
        result: Result data from the task
        error: Error message if the task failed
    """
    succeeded: bool
    result: Any
    error: Optional[str]


class RunAgentRequest(TypedDict, total=False):
    """
    Request parameters for running a named agent.
    
    Attributes:
        agent_name: Name of the agent to run (required)
        session_id: Session to run the agent in (required)
        variables: Dictionary of variables to pass to the agent
    """
    agent_name: str
    session_id: str
    variables: Dict[str, Any]


class RunAgentResponse(TypedDict):
    """
    Response from running a named agent.
    
    Attributes:
        succeeded: Whether the agent completed successfully
        session_id: The session ID where the agent ran
        agent_name: Name of the agent that ran
        result: Result data from the agent
    """
    succeeded: bool
    session_id: str
    agent_name: str
    result: Any


class GetSessionStoreResponse(TypedDict):
    """
    Response from getting session store data.
    
    Attributes:
        succeeded: Whether the request succeeded
        session_store: Dictionary containing session data
        error: Error message if the request failed
    """
    succeeded: bool
    session_store: Optional[Dict[str, Any]]
    error: Optional[str]


class DownloadSessionFilesRequest(TypedDict, total=False):
    """
    Request parameters for downloading session files.
    
    Attributes:
        session_id: Session to download files from (required)
        filename: Optional specific filename to download
    """
    session_id: str
    filename: str


class DownloadSessionFilesErrorResponse(TypedDict):
    """
    Error response from downloading session files.
    
    Attributes:
        succeeded: Always False for error responses
        error: Error message describing what went wrong
    """
    succeeded: bool
    error: str


class TwoFactorConfig(TypedDict, total=False):
    """
    Configuration for 2FA authentication.
    
    Attributes:
        seed: The 2FA seed/secret (required)
        name: Optional name for this 2FA config
        partial_url: Optional partial URL to match for auto-detection
    """
    seed: str
    name: str
    partial_url: str


class Add2FAConfigRequest(TypedDict, total=False):
    """
    Request parameters for adding a 2FA configuration.
    
    Attributes:
        seed: The 2FA seed/secret (required)
        name: Optional name for this 2FA config
        partial_url: Optional partial URL to match for auto-detection
    """
    seed: str
    name: str
    partial_url: str


class Add2FAConfigResponse(TypedDict):
    """
    Response from adding a 2FA configuration.
    
    Attributes:
        succeeded: Whether the config was added successfully
        added_config: The configuration that was added
        total_configs: Total number of 2FA configs after adding
        all_configs: List of all 2FA configurations
        error: Error message if the request failed
    """
    succeeded: bool
    added_config: Optional[Any]
    total_configs: Optional[int]
    all_configs: Optional[List[Any]]
    error: Optional[str]