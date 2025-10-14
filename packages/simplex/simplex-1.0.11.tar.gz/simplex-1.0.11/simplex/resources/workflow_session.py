"""
WorkflowSession class for managing Simplex workflow sessions.

This module provides the WorkflowSession class which represents an active
workflow session and provides methods for interacting with it.
"""

from typing import Any, Dict, List, Optional

from simplex.errors import SimplexError, WorkflowError
from simplex.http_client import HttpClient
from simplex.types import AgenticResponse, RunAgentResponse


class WorkflowSession:
    """
    Represents an active workflow session.
    
    A WorkflowSession provides methods for interacting with a running workflow,
    including navigation, agent execution, and session management. It can be used
    as a context manager for automatic cleanup.
    
    Example:
        >>> with client.create_workflow_session(name="test", url="https://example.com") as session:
        ...     session.goto("https://example.com/login")
        ...     session.run_agent("Login Agent", variables={"username": "user"})
        ...     # Session automatically closed when exiting the with block
    
    Attributes:
        session_id: Unique identifier for this session
        workflow_id: ID of the workflow
        livestream_url: URL to view the live browser session
        connect_url: URL to connect to the session
        vnc_url: URL for VNC access
    """
    
    def __init__(
        self,
        http_client: HttpClient,
        session_data: Dict[str, str]
    ):
        """
        Initialize a WorkflowSession.
        
        Args:
            http_client: HTTP client for making API requests
            session_data: Dictionary containing session information
        """
        self._http_client = http_client
        self.session_id = session_data['sessionId']
        self.workflow_id = session_data['workflowId']
        self.livestream_url = session_data['livestreamUrl']
        self.connect_url = session_data['connectUrl']
        self.vnc_url = session_data['vncUrl']
        self._closed = False
    
    def __enter__(self) -> 'WorkflowSession':
        """
        Enter the context manager.
        
        Returns:
            This session instance
        """
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit the context manager and close the session.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        self.close()
    
    def goto(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a specific URL within the session.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Response from the navigation action
            
        Raises:
            WorkflowError: If navigation fails
        """
        if self._closed:
            raise WorkflowError("Cannot navigate - session is closed", session_id=self.session_id)
        
        try:
            response = self._http_client.post(
                '/agentic',
                data={
                    'task': f'Navigate to {url}',
                    'session_id': self.session_id,
                    'max_steps': 1
                }
            )
            
            if not response.get('succeeded'):
                raise WorkflowError(
                    f"Failed to navigate to {url}: {response.get('error', 'Unknown error')}",
                    session_id=self.session_id
                )
            
            return response
        except SimplexError:
            raise
        except Exception as e:
            raise WorkflowError(
                f"Failed to navigate to {url}: {str(e)}",
                session_id=self.session_id
            )
    
    def agentic(
        self,
        task: str,
        max_steps: Optional[int] = None,
        actions_to_exclude: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> AgenticResponse:
        """
        Execute an agentic task within this session.
        
        This method allows you to give natural language instructions to an agent
        that will execute them within the browser session.
        
        Args:
            task: Natural language description of what to do
            max_steps: Maximum number of steps the agent can take (optional)
            actions_to_exclude: List of action types to exclude (optional)
            variables: Dictionary of variables to use in the task (optional)
            
        Returns:
            Response containing task results
            
        Raises:
            WorkflowError: If the task fails
            
        Example:
            >>> session.agentic("Click the login button and enter credentials")
        """
        if self._closed:
            raise WorkflowError("Cannot execute task - session is closed", session_id=self.session_id)
        
        import json
        
        request_data = {
            'task': task,
            'session_id': self.session_id
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
                    data={'session_id': self.session_id, 'task': task}
                )
            
            return response
        except SimplexError:
            raise
        except Exception as e:
            raise SimplexError(
                f"Failed to run agent task: {str(e)}",
                status_code=500,
                data={'session_id': self.session_id, 'task': task}
            )
    
    def run_agent(
        self,
        agent_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> RunAgentResponse:
        """
        Run a named agent within this session.
        
        Named agents are pre-configured agents that can be executed by name.
        
        Args:
            agent_name: Name of the agent to run
            variables: Dictionary of variables to pass to the agent (optional)
            
        Returns:
            Response containing agent execution results
            
        Raises:
            SimplexError: If the agent execution fails
            
        Example:
            >>> session.run_agent("Login Agent", variables={"username": "user@example.com"})
        """
        if self._closed:
            raise WorkflowError("Cannot run agent - session is closed", session_id=self.session_id)
        
        request_data = {
            'agent_name': agent_name,
            'session_id': self.session_id
        }
        
        if variables:
            request_data['variables'] = variables
        
        try:
            response = self._http_client.post('/run_agent', data=request_data)
            
            if not response.get('succeeded'):
                raise SimplexError(
                    f"Agent run failed for {agent_name}",
                    status_code=500,
                    data={'agent_name': agent_name, 'session_id': self.session_id}
                )
            
            return response
        except SimplexError:
            raise
        except Exception as e:
            raise SimplexError(
                f"Failed to run agent: {str(e)}",
                status_code=500,
                data={'agent_name': agent_name, 'session_id': self.session_id}
            )
    
    def start_capture(self) -> Dict[str, bool]:
        """
        Start capture mode for this session.
        
        Capture mode records browser actions for later playback.
        
        Returns:
            Response indicating success
            
        Raises:
            WorkflowError: If starting capture mode fails
        """
        if self._closed:
            raise WorkflowError("Cannot start capture - session is closed", session_id=self.session_id)
        
        try:
            response = self._http_client.post(
                '/start_capture_mode',
                data={'session_id': self.session_id}
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to start capture mode: {str(e)}",
                session_id=self.session_id
            )
    
    def stop_capture(self) -> Dict[str, bool]:
        """
        Stop capture mode for this session.
        
        Returns:
            Response indicating success
            
        Raises:
            WorkflowError: If stopping capture mode fails
        """
        if self._closed:
            raise WorkflowError("Cannot stop capture - session is closed", session_id=self.session_id)
        
        try:
            response = self._http_client.post(
                '/stop_capture_mode',
                data={'session_id': self.session_id}
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to stop capture mode: {str(e)}",
                session_id=self.session_id
            )
    
    def close(self) -> Dict[str, Any]:
        """
        Close this workflow session.
        
        This releases resources associated with the session. Once closed,
        the session cannot be used for further operations.
        
        Returns:
            Response from closing the session
            
        Raises:
            WorkflowError: If closing the session fails
        """
        if self._closed:
            return {'succeeded': True, 'message': 'Session already closed'}
        
        try:
            response = self._http_client.post(
                '/close_workflow_session',
                data={'session_id': self.session_id}
            )
            self._closed = True
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to close workflow session: {str(e)}",
                session_id=self.session_id
            )
    
    @property
    def is_closed(self) -> bool:
        """
        Check if the session is closed.
        
        Returns:
            True if the session is closed, False otherwise
        """
        return self._closed
    
    def __repr__(self) -> str:
        """Return a string representation of the session."""
        status = "closed" if self._closed else "open"
        return f"WorkflowSession(session_id='{self.session_id}', status='{status}')"