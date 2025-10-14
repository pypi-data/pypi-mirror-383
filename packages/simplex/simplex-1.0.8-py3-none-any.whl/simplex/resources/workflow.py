"""
Workflow resource for the Simplex SDK.

This module provides the Workflow class which handles all workflow-related
operations including execution, session management, and agent tasks.
"""

import json
from typing import Any, Dict, List, Optional

from simplex.errors import SimplexError, WorkflowError
from simplex.http_client import HttpClient
from simplex.types import (
    AgenticResponse,
    CreateWorkflowSessionResponse,
    RunAgentResponse,
    RunWorkflowResponse,
    WorkflowStatusResponse,
    WorkflowVariables,
)


class Workflow:
    """
    Resource class for workflow operations.
    
    This class provides methods for:
    - Running workflows with variables
    - Creating and managing workflow sessions
    - Executing agent tasks
    - Managing workflow segments
    - Controlling capture mode
    
    Attributes:
        _http_client: HTTP client for making API requests
    """
    
    def __init__(self, http_client: HttpClient):
        """
        Initialize the Workflow resource.
        
        Args:
            http_client: HTTP client instance for API communication
        """
        self._http_client = http_client
    
    def run(
        self,
        workflow_id: str,
        variables: Optional[WorkflowVariables] = None,
        metadata: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> RunWorkflowResponse:
        """
        Execute a workflow by ID.
        
        This method starts a workflow execution with the provided parameters.
        The workflow will run asynchronously and you can check its status
        using the get_status() method with the returned session_id.
        
        Args:
            workflow_id: Unique identifier of the workflow to run
            variables: Dictionary of variables to pass to the workflow (optional)
            metadata: Optional metadata string to attach to the run
            webhook_url: Optional webhook URL for status updates
            
        Returns:
            Response containing session_id and execution details
            
        Raises:
            WorkflowError: If the workflow execution fails to start
            
        Example:
            >>> result = client.workflows.run(
            ...     "workflow-123",
            ...     variables={"username": "user@example.com", "product_id": "456"}
            ... )
            >>> print(f"Started workflow with session: {result['session_id']}")
        """
        request_data = {
            'workflow_id': workflow_id,
        }
        
        if variables:
            request_data['variables'] = variables
        
        if metadata:
            request_data['metadata'] = metadata
        
        if webhook_url:
            request_data['webhook_url'] = webhook_url
        
        try:
            response = self._http_client.post('/run_workflow', data=request_data)
            
            if not response.get('succeeded'):
                raise WorkflowError(
                    response.get('message') or 'Workflow execution failed',
                    workflow_id=workflow_id,
                    session_id=response.get('session_id')
                )
            
            return response
        except WorkflowError:
            raise
        except Exception as e:
            raise WorkflowError(
                f"Failed to run workflow: {str(e)}",
                workflow_id=workflow_id
            )
    
    def get_status(self, session_id: str) -> WorkflowStatusResponse:
        """
        Get the status of a workflow execution.
        
        This method retrieves the current status of a workflow, including
        whether it has completed and what actions have been taken.
        
        Args:
            session_id: Session ID returned from run()
            
        Returns:
            Status response with completion info and action history
            
        Raises:
            WorkflowError: If status check fails
            
        Example:
            >>> status = client.workflows.get_status("session-123")
            >>> if status['completed']:
            ...     print(f"Workflow completed with {status['total_actions']} actions")
        """
        try:
            response = self._http_client.get(
                f'/run_workflow_status?session_id={session_id}'
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to get workflow status: {str(e)}",
                session_id=session_id
            )
    
    def create_workflow_session(
        self,
        workflow_name: str,
        url: str,
        proxies: bool = False,
        session_data: Optional[Any] = None
    ) -> CreateWorkflowSessionResponse:
        """
        Create a new workflow session.
        
        This creates a new browser session that can be controlled programmatically.
        Unlike run(), this gives you direct control over the session through
        agent tasks and actions.
        
        Args:
            workflow_name: Name for this workflow session
            url: Starting URL for the browser session
            proxies: Whether to use proxies (default: False)
            session_data: Optional data to associate with the session
            
        Returns:
            Response containing session details and access URLs
            
        Raises:
            WorkflowError: If session creation fails
            
        Example:
            >>> session = client.workflows.create_workflow_session(
            ...     "test-session",
            ...     "https://example.com",
            ...     proxies=False
            ... )
            >>> print(f"Session ID: {session['session_id']}")
            >>> print(f"Livestream: {session['livestream_url']}")
        """
        # Ensure URL has protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        request_data = {
            'workflow_name': workflow_name,
            'url': url,
            'proxies': proxies
        }
        
        if session_data is not None:
            request_data['session_data'] = json.dumps(session_data)
        
        try:
            response = self._http_client.post(
                '/create_workflow_session',
                data=request_data
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to create workflow session: {str(e)}"
            )
    
    def start_segment(
        self,
        workflow_id: str,
        segment_name: str
    ) -> Dict[str, Any]:
        """
        Start a new segment within a workflow.
        
        Segments allow you to organize workflow actions into logical groups.
        
        Args:
            workflow_id: ID of the workflow
            segment_name: Name for the segment
            
        Returns:
            Response containing segment_id if successful
            
        Raises:
            WorkflowError: If starting the segment fails
            
        Example:
            >>> result = client.workflows.start_segment("workflow-123", "login-phase")
            >>> segment_id = result['segment_id']
        """
        request_data = {
            'workflow_id': workflow_id,
            'segment_name': segment_name
        }
        
        try:
            response = self._http_client.post('/start_segment', data=request_data)
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to start segment: {str(e)}",
                workflow_id=workflow_id
            )
    
    def finish_segment(self, workflow_id: str) -> Dict[str, Any]:
        """
        Finish the current segment within a workflow.
        
        This completes the current segment and returns any recorded actions.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Response containing segment actions if successful
            
        Raises:
            WorkflowError: If finishing the segment fails
            
        Example:
            >>> result = client.workflows.finish_segment("workflow-123")
            >>> actions = result.get('segment_actions', [])
        """
        request_data = {
            'workflow_id': workflow_id
        }
        
        try:
            response = self._http_client.post('/finish_segment', data=request_data)
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to finish segment: {str(e)}",
                workflow_id=workflow_id
            )
    
    def start_capture(self, session_id: str) -> Dict[str, bool]:
        """
        Start capture mode for a session.
        
        Capture mode records all browser actions for later playback or analysis.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Response indicating success
            
        Raises:
            WorkflowError: If starting capture mode fails
            
        Example:
            >>> result = client.workflows.start_capture("session-123")
            >>> if result['succeeded']:
            ...     print("Capture mode started")
        """
        request_data = {
            'session_id': session_id
        }
        
        try:
            response = self._http_client.post('/start_capture_mode', data=request_data)
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to start capture mode: {str(e)}",
                session_id=session_id
            )
    
    def stop_capture(self, session_id: str) -> Dict[str, bool]:
        """
        Stop capture mode for a session.
        
        This stops recording browser actions.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Response indicating success
            
        Raises:
            WorkflowError: If stopping capture mode fails
            
        Example:
            >>> result = client.workflows.stop_capture("session-123")
            >>> if result['succeeded']:
            ...     print("Capture mode stopped")
        """
        request_data = {
            'session_id': session_id
        }
        
        try:
            response = self._http_client.post('/stop_capture_mode', data=request_data)
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to stop capture mode: {str(e)}",
                session_id=session_id
            )
    
    def close_workflow_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close a workflow session.
        
        This releases all resources associated with the session.
        
        Args:
            session_id: ID of the session to close
            
        Returns:
            Response indicating success
            
        Raises:
            WorkflowError: If closing the session fails
            
        Example:
            >>> result = client.workflows.close_workflow_session("session-123")
            >>> print(result.get('message'))
        """
        request_data = {
            'session_id': session_id
        }
        
        try:
            response = self._http_client.post(
                '/close_workflow_session',
                data=request_data
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to close workflow session: {str(e)}",
                session_id=session_id
            )
    
    def agentic(
        self,
        task: str,
        session_id: str,
        max_steps: Optional[int] = None,
        actions_to_exclude: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> AgenticResponse:
        """
        Execute an agentic task within a session.
        
        This method allows you to give natural language instructions to an AI agent
        that will execute them within a browser session.
        
        Args:
            task: Natural language description of what to do
            session_id: Session where the task should be executed
            max_steps: Maximum number of steps the agent can take (optional)
            actions_to_exclude: List of action types to exclude (optional)
            variables: Dictionary of variables to use in the task (optional)
            
        Returns:
            Response containing task results
            
        Raises:
            SimplexError: If the task execution fails
            
        Example:
            >>> result = client.workflows.agentic(
            ...     "Find the login button and click it",
            ...     "session-123",
            ...     max_steps=10
            ... )
            >>> if result['succeeded']:
            ...     print("Task completed:", result['result'])
        """
        request_data = {
            'task': task,
            'session_id': session_id
        }
        
        if max_steps is not None:
            request_data['max_steps'] = max_steps
        
        if actions_to_exclude:
            request_data['actions_to_exclude'] = actions_to_exclude
        
        if variables:
            request_data['variables'] = json.dumps(variables)
        
        try:
            response = self._http_client.post('/agentic', data=request_data)
            
            if not response.get('succeeded') and response.get('error'):
                raise SimplexError(
                    f"Agent task failed: {response['error']}",
                    status_code=500,
                    data={'session_id': session_id, 'task': task}
                )
            
            return response
        except SimplexError:
            raise
        except Exception as e:
            raise SimplexError(
                f"Failed to run agent task: {str(e)}",
                status_code=500,
                data={'session_id': session_id, 'task': task}
            )
    
    def run_agent(
        self,
        agent_name: str,
        session_id: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> RunAgentResponse:
        """
        Run a named agent within a session.
        
        Named agents are pre-configured agents that can be executed by name.
        They encapsulate common workflows or tasks.
        
        Args:
            agent_name: Name of the agent to run
            session_id: Session where the agent should run
            variables: Dictionary of variables to pass to the agent (optional)
            
        Returns:
            Response containing agent execution results
            
        Raises:
            SimplexError: If the agent execution fails
            
        Example:
            >>> result = client.workflows.run_agent(
            ...     "Login Agent",
            ...     "session-123",
            ...     variables={"username": "user@example.com", "password": "secret"}
            ... )
            >>> if result['succeeded']:
            ...     print("Agent completed:", result['result'])
        """
        request_data = {
            'agent_name': agent_name,
            'session_id': session_id
        }
        
        if variables:
            request_data['variables'] = variables
        
        try:
            response = self._http_client.post('/run_agent', data=request_data)
            
            if not response.get('succeeded'):
                raise SimplexError(
                    f"Agent run failed for {agent_name}",
                    status_code=500,
                    data={'agent_name': agent_name, 'session_id': session_id}
                )
            
            return response
        except SimplexError:
            raise
        except Exception as e:
            raise SimplexError(
                f"Failed to run agent: {str(e)}",
                status_code=500,
                data={'agent_name': agent_name, 'session_id': session_id}
            )