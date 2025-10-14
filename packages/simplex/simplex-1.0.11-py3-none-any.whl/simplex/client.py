"""
Main SimplexClient class for the Simplex SDK.

This module provides the SimplexClient, which is the primary entry point
for interacting with the Simplex API.
"""

import json
from typing import Any, Dict, Optional

from simplex.errors import WorkflowError
from simplex.http_client import HttpClient
from simplex.resources.workflow import Workflow
from simplex.resources.workflow_session import WorkflowSession
from simplex.types import (
    Add2FAConfigResponse,
    CreateWorkflowSessionResponse,
    GetSessionStoreResponse,
    SimplexClientOptions,
)


class SimplexClient:
    """
    Main client for interacting with the Simplex API.
    
    This is the primary entry point for the SDK. It provides access to all
    Simplex API functionality through resource classes and utility methods.
    
    Example:
        >>> from simplex import SimplexClient
        >>> client = SimplexClient(api_key="your-api-key")
        >>> 
        >>> # Run a workflow
        >>> result = client.workflows.run("workflow-id")
        >>> 
        >>> # Create a workflow session
        >>> with client.create_workflow_session("test", "https://example.com") as session:
        ...     session.goto("https://example.com/login")
        ...     session.run_agent("Login Agent")
    
    Attributes:
        workflows: Resource for workflow operations
    """
    
    def __init__(
        self,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1,
        base_url: str = "https://api.simplex.sh"
    ):
        """
        Initialize the Simplex client.
        
        Args:
            api_key: Your Simplex API key (required)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 1)
            base_url: Base URL for the API (default: "https://api.simplex.sh")
            
        Raises:
            ValueError: If api_key is not provided
            
        Example:
            >>> client = SimplexClient(
            ...     api_key="your-api-key",
            ...     timeout=60,
            ...     max_retries=5
            ... )
        """
        if not api_key:
            raise ValueError("api_key is required")
        
        # Initialize HTTP client
        self._http_client = HttpClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            retry_attempts=max_retries,
            retry_delay=retry_delay
        )
        
        # Initialize resource classes
        self.workflows = Workflow(self._http_client)
    
    def create_workflow_session(
        self,
        name: str,
        url: str,
        proxies: bool = False,
        session_data: Optional[Any] = None
    ) -> WorkflowSession:
        """
        Create a new workflow session with context manager support.
        
        This method creates a new browser session that can be controlled
        programmatically. The returned WorkflowSession can be used as a
        context manager for automatic cleanup.
        
        Args:
            name: Name for this workflow session
            url: Starting URL for the browser session
            proxies: Whether to use proxies (default: False)
            session_data: Optional data to associate with the session
            
        Returns:
            WorkflowSession object for interacting with the session
            
        Raises:
            WorkflowError: If session creation fails
            
        Example:
            >>> # Using as a context manager (recommended)
            >>> with client.create_workflow_session("test", "https://example.com") as session:
            ...     session.goto("https://example.com/login")
            ...     session.run_agent("Login Agent")
            ...     # Session automatically closed when exiting the with block
            >>> 
            >>> # Or manage manually
            >>> session = client.create_workflow_session("test", "https://example.com")
            >>> try:
            ...     session.goto("https://example.com/login")
            ... finally:
            ...     session.close()
        """
        # Ensure URL has protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        request_data = {
            'workflow_name': name,
            'url': url,
            'proxies': proxies
        }
        
        if session_data is not None:
            request_data['session_data'] = json.dumps(session_data)
        
        try:
            response: CreateWorkflowSessionResponse = self._http_client.post(
                '/create_workflow_session',
                data=request_data
            )
            
            # Create and return WorkflowSession object
            return WorkflowSession(
                self._http_client,
                {
                    'sessionId': response['session_id'],
                    'workflowId': response['workflow_id'],
                    'livestreamUrl': response['livestream_url'],
                    'connectUrl': response['connect_url'],
                    'vncUrl': response['vnc_url']
                }
            )
        except Exception as e:
            raise WorkflowError(
                f"Failed to create workflow session: {str(e)}"
            )
    
    def get_session_store(self, session_id: str) -> GetSessionStoreResponse:
        """
        Retrieve session store data for a specific session.
        
        The session store contains data that was saved during workflow execution.
        
        Args:
            session_id: ID of the session to retrieve store data for
            
        Returns:
            Response containing session store data
            
        Raises:
            WorkflowError: If retrieving session store fails
            
        Example:
            >>> store = client.get_session_store("session-123")
            >>> if store['succeeded']:
            ...     data = store['session_store']
            ...     print(f"Session data: {data}")
        """
        try:
            response: GetSessionStoreResponse = self._http_client.post(
                '/get_session_store',
                data={'session_id': session_id}
            )
            return response
        except Exception as e:
            raise WorkflowError(
                f"Failed to get session store: {str(e)}",
                session_id=session_id
            )
    
    def download_session_files(
        self,
        session_id: str,
        filename: Optional[str] = None
    ) -> bytes:
        """
        Download files from a session.
        
        This method downloads files that were created or downloaded during
        a workflow session. If no filename is specified, all files are
        downloaded as a zip archive.
        
        Args:
            session_id: ID of the session to download files from
            filename: Optional specific filename to download
            
        Returns:
            File content as bytes
            
        Raises:
            WorkflowError: If file download fails
            
        Example:
            >>> # Download all files as zip
            >>> zip_data = client.download_session_files("session-123")
            >>> with open("session_files.zip", "wb") as f:
            ...     f.write(zip_data)
            >>> 
            >>> # Download specific file
            >>> file_data = client.download_session_files("session-123", "report.pdf")
            >>> with open("report.pdf", "wb") as f:
            ...     f.write(file_data)
        """
        try:
            params = {'session_id': session_id}
            if filename:
                params['filename'] = filename
            
            content = self._http_client.download_file('/download_session_files', params=params)
            
            # Check if the response is a JSON error by trying to decode and parse it
            try:
                text = content.decode('utf-8')
                data = json.loads(text)
                if isinstance(data, dict) and data.get('succeeded') is False:
                    raise WorkflowError(
                        data.get('error') or 'Failed to download session files',
                        session_id=session_id
                    )
            except (UnicodeDecodeError, json.JSONDecodeError):
                # If decoding/parsing fails, it's binary data (the file), which is what we want
                pass
            
            return content
        except WorkflowError:
            raise
        except Exception as e:
            raise WorkflowError(
                f"Failed to download session files: {str(e)}",
                session_id=session_id
            )
    
    def add_2fa_config(
        self,
        seed: str,
        name: Optional[str] = None,
        partial_url: Optional[str] = None
    ) -> Add2FAConfigResponse:
        """
        Add a 2FA (Two-Factor Authentication) configuration.
        
        This allows workflows to automatically handle 2FA authentication
        when encountering sites that require it.
        
        Args:
            seed: The 2FA seed/secret key
            name: Optional name for this 2FA configuration
            partial_url: Optional partial URL to match for auto-detection
            
        Returns:
            Response with configuration details
            
        Raises:
            WorkflowError: If adding the configuration fails
            
        Example:
            >>> result = client.add_2fa_config(
            ...     seed="JBSWY3DPEHPK3PXP",
            ...     name="My Service",
            ...     partial_url="example.com"
            ... )
            >>> if result['succeeded']:
            ...     print(f"Total configs: {result['total_configs']}")
        """
        request_data = {'seed': seed}
        
        if name:
            request_data['name'] = name
        
        if partial_url:
            request_data['partial_url'] = partial_url
        
        try:
            response: Add2FAConfigResponse = self._http_client.post_json(
                '/add_2fa_config',
                data=request_data
            )
            
            if not response.get('succeeded') and response.get('error'):
                raise WorkflowError(
                    f"Failed to add 2FA config: {response['error']}"
                )
            
            return response
        except WorkflowError:
            raise
        except Exception as e:
            raise WorkflowError(
                f"Failed to add 2FA config: {str(e)}"
            )
    
    def update_api_key(self, api_key: str) -> None:
        """
        Update the API key used for authentication.
        
        This allows you to change the API key without creating a new client instance.
        
        Args:
            api_key: New API key to use
            
        Example:
            >>> client.update_api_key("new-api-key")
        """
        self._http_client.update_api_key(api_key)
    
    def set_custom_header(self, key: str, value: str) -> None:
        """
        Set a custom header to be included with all requests.
        
        Args:
            key: Header name
            value: Header value
            
        Example:
            >>> client.set_custom_header("X-Custom-Header", "custom-value")
        """
        self._http_client.set_header(key, value)
    
    def remove_custom_header(self, key: str) -> None:
        """
        Remove a custom header.
        
        Args:
            key: Header name to remove
            
        Example:
            >>> client.remove_custom_header("X-Custom-Header")
        """
        self._http_client.remove_header(key)