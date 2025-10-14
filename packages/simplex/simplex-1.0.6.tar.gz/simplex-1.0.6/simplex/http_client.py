"""
HTTP client for the Simplex SDK.

This module provides a robust HTTP client with automatic retry logic,
error handling, and support for various request types.
"""

import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from simplex.errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    SimplexError,
    ValidationError,
)


class HttpClient:
    """
    HTTP client with retry logic and error handling.
    
    This client handles all communication with the Simplex API, including:
    - Automatic retry with exponential backoff
    - Error mapping to custom exceptions
    - Support for form-encoded and JSON requests
    - File downloads
    - Custom header management
    
    Attributes:
        base_url: Base URL for API requests
        api_key: API key for authentication
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts for failed requests
        retry_delay: Base delay between retries in seconds
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: int = 1,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the HTTP client.
        
        Args:
            base_url: Base URL for the API (e.g., 'https://api.simplex.sh')
            api_key: Your Simplex API key
            timeout: Request timeout in seconds (default: 30)
            retry_attempts: Maximum number of retry attempts (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1)
            headers: Additional headers to include with all requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Create a session with retry configuration
        self.session = requests.Session()
        
        # Configure default headers
        self.session.headers.update({
            'X-API-Key': api_key,
            'User-Agent': 'Simplex-Python-SDK/1.0.0',
        })
        
        if headers:
            self.session.headers.update(headers)
        
        # Configure retry strategy for specific status codes
        retry_strategy = Retry(
            total=0,  # We'll handle retries manually for more control
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _should_retry(self, response: Optional[requests.Response]) -> bool:
        """
        Determine if a request should be retried.
        
        Args:
            response: The response object (None for network errors)
            
        Returns:
            True if the request should be retried, False otherwise
        """
        if response is None:
            # Network error - should retry
            return True
        
        # Retry on rate limit, service unavailable, or server errors
        return response.status_code in [429, 503] or response.status_code >= 500
    
    def _handle_error(self, response: requests.Response) -> SimplexError:
        """
        Convert HTTP errors to appropriate exception types.
        
        Args:
            response: The error response
            
        Returns:
            Appropriate SimplexError subclass for the error type
        """
        status_code = response.status_code
        
        # Try to extract error message from response
        try:
            data = response.json()
            if isinstance(data, dict):
                message = data.get('message') or data.get('error') or 'An error occurred'
            else:
                message = str(data)
        except ValueError:
            message = response.text or 'An error occurred'
        
        # Map status codes to exception types
        if status_code == 400:
            return ValidationError(message, data=response.json() if response.text else None)
        elif status_code in [401, 403]:
            return AuthenticationError(message)
        elif status_code == 429:
            # Extract retry-after header if present
            retry_after = response.headers.get('Retry-After')
            retry_after_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            return RateLimitError(message, retry_after=retry_after_seconds)
        else:
            return SimplexError(message, status_code=status_code, data=response.json() if response.text else None)
    
    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> requests.Response:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers for this request
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
            
        Raises:
            SimplexError: If the request fails after all retries
        """
        url = f"{self.base_url}{path}"
        attempt = 0
        last_exception = None
        
        while attempt <= self.retry_attempts:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check for HTTP errors
                if not response.ok:
                    error = self._handle_error(response)
                    
                    # Retry if appropriate
                    if self._should_retry(response) and attempt < self.retry_attempts:
                        attempt += 1
                        time.sleep(self.retry_delay * attempt)  # Exponential backoff
                        continue
                    
                    raise error
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = NetworkError(str(e))
                
                # Retry network errors
                if attempt < self.retry_attempts:
                    attempt += 1
                    time.sleep(self.retry_delay * attempt)
                    continue
                
                raise last_exception
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        raise NetworkError("Request failed after all retries")
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a GET request.
        
        Args:
            path: API endpoint path
            params: Query parameters
            
        Returns:
            Parsed JSON response
        """
        response = self._make_request('GET', path, params=params)
        return response.json()
    
    def post(
        self, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a POST request with form-encoded data.
        
        This method sends data as application/x-www-form-urlencoded,
        which is the default format for the Simplex API.
        
        Args:
            path: API endpoint path
            data: Form data to send
            headers: Additional headers
            
        Returns:
            Parsed JSON response
        """
        # Convert data to form-encoded format
        form_data = {}
        if data:
            for key, value in data.items():
                if value is not None:
                    # Convert complex objects to JSON strings
                    if isinstance(value, (dict, list)):
                        import json
                        form_data[key] = json.dumps(value)
                    else:
                        form_data[key] = str(value)
        
        request_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if headers:
            request_headers.update(headers)
        
        response = self._make_request(
            'POST',
            path,
            data=urlencode(form_data) if form_data else None,
            headers=request_headers
        )
        return response.json()
    
    def post_json(
        self, 
        path: str, 
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a POST request with JSON data.
        
        Args:
            path: API endpoint path
            data: Data to send as JSON
            headers: Additional headers
            
        Returns:
            Parsed JSON response
        """
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        
        response = self._make_request(
            'POST',
            path,
            json=data,
            headers=request_headers
        )
        return response.json()
    
    def put(
        self, 
        path: str, 
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a PUT request.
        
        Args:
            path: API endpoint path
            data: Data to send
            headers: Additional headers
            
        Returns:
            Parsed JSON response
        """
        response = self._make_request('PUT', path, json=data, headers=headers)
        return response.json()
    
    def patch(
        self, 
        path: str, 
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make a PATCH request.
        
        Args:
            path: API endpoint path
            data: Data to send
            headers: Additional headers
            
        Returns:
            Parsed JSON response
        """
        response = self._make_request('PATCH', path, json=data, headers=headers)
        return response.json()
    
    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make a DELETE request.
        
        Args:
            path: API endpoint path
            headers: Additional headers
            
        Returns:
            Parsed JSON response
        """
        response = self._make_request('DELETE', path, headers=headers)
        return response.json()
    
    def download_file(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Download a file from the API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            
        Returns:
            File content as bytes
        """
        response = self._make_request('GET', path, params=params)
        return response.content
    
    def set_header(self, key: str, value: str) -> None:
        """
        Set a custom header for all requests.
        
        Args:
            key: Header name
            value: Header value
        """
        self.session.headers[key] = value
    
    def remove_header(self, key: str) -> None:
        """
        Remove a custom header.
        
        Args:
            key: Header name to remove
        """
        self.session.headers.pop(key, None)
    
    def update_api_key(self, api_key: str) -> None:
        """
        Update the API key used for authentication.
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
        self.set_header('X-API-Key', api_key)