# Simplex Python SDK

Official Python SDK for the [Simplex API](https://simplex.sh) - A powerful workflow automation platform for browser-based tasks.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🚀 Simple and intuitive API
- 🔄 Automatic retry logic with exponential backoff
- 🎯 Type hints for better IDE support
- 🔐 Built-in error handling
- 📦 Context manager support for automatic cleanup
- 🤖 Support for agentic workflows and named agents
- 📁 File download capabilities
- 🔑 2FA configuration management

## Installation

Install the Simplex SDK using pip:

```bash
pip install simplex
```

## Quick Start

```python
from simplex import SimplexClient

# Initialize the client
client = SimplexClient(api_key='your-api-key')

# Run a workflow with variables
result = client.workflows.run(
    'workflow-id',
    variables={'username': 'user@example.com'}
)

print(f"Workflow started: {result['session_id']}")
```

## Usage Examples

### Creating a Workflow Session

Use workflow sessions for more control over browser automation:

```python
from simplex import SimplexClient

client = SimplexClient(api_key='your-api-key')

# Using context manager for automatic cleanup
with client.create_workflow_session(
    name='my-workflow',
    url='https://example.com'
) as session:
    print(f'Session ID: {session.session_id}')
    print(f'Livestream URL: {session.livestream_url}')
    
    # Navigate to a page
    session.goto('https://example.com/login')
    
    # Run a named agent
    session.run_agent('Login Agent', variables={
        'username': 'user@example.com',
        'password': 'secret'
    })
    
    # Execute an agentic task
    session.agentic('Click the submit button and wait for confirmation')
    
    # Session automatically closes when exiting the with block
```

### Running a Workflow

Execute pre-built workflows with variables:

```python
from simplex import SimplexClient, WorkflowError

client = SimplexClient(api_key='your-api-key')

try:
    # Run workflow with variables
    result = client.workflows.run(
        'workflow-id',
        variables={
            'email': 'user@example.com',
            'product_id': '12345'
        },
        metadata='Order processing workflow'
    )
    
    print(f"Success: {result['succeeded']}")
    print(f"Session ID: {result['session_id']}")
    
    # Check workflow status
    status = client.workflows.get_status(result['session_id'])
    print(f"Completed: {status['completed']}")
    print(f"Total actions: {status['total_actions']}")
    
except WorkflowError as e:
    print(f"Workflow failed: {e.message}")
```

### Using Agentic Tasks

Execute natural language instructions:

```python
# Within a workflow session
session.agentic(
    'Navigate to the invoices page and download the latest invoice',
    max_steps=10
)

# Or using the workflows resource
client.workflows.agentic(
    task='Find and click the login button',
    session_id='session-id',
    max_steps=5
)
```

### Downloading Session Files

Download files created during workflow execution:

```python
from simplex import SimplexClient

client = SimplexClient(api_key='your-api-key')

# Download all files as a zip
zip_data = client.download_session_files('session-id')
with open('session_files.zip', 'wb') as f:
    f.write(zip_data)

# Download a specific file
file_data = client.download_session_files('session-id', filename='report.pdf')
with open('report.pdf', 'wb') as f:
    f.write(file_data)
```

### Adding 2FA Configuration

Configure automatic 2FA handling:

```python
from simplex import SimplexClient

client = SimplexClient(api_key='your-api-key')

result = client.add_2fa_config(
    seed='JBSWY3DPEHPK3PXP',
    name='My Service',
    partial_url='example.com'
)

print(f"Total configs: {result['total_configs']}")
```

### Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from simplex import (
    SimplexClient,
    SimplexError,
    WorkflowError,
    AuthenticationError,
    RateLimitError,
    NetworkError
)

client = SimplexClient(api_key='your-api-key')

try:
    result = client.workflows.run('workflow-id')
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except WorkflowError as e:
    print(f"Workflow error: {e.message}")
    print(f"Workflow ID: {e.workflow_id}")
    print(f"Session ID: {e.session_id}")
except NetworkError as e:
    print(f"Network error: {e.message}")
except SimplexError as e:
    print(f"General error: {e.message}")
```

## Configuration

### Environment Variables

You can use environment variables for configuration:

```python
import os
from simplex import SimplexClient

api_key = os.getenv('SIMPLEX_API_KEY')
client = SimplexClient(api_key=api_key)
```

Example `.env` file:

```bash
SIMPLEX_API_KEY=your-api-key
WORKFLOW_ID=your-workflow-id
```

### Client Options

Customize client behavior with initialization parameters:

```python
from simplex import SimplexClient

client = SimplexClient(
    api_key='your-api-key',
    timeout=60,           # Request timeout in seconds
    max_retries=5,        # Maximum retry attempts
    retry_delay=2,        # Delay between retries in seconds
    base_url='https://api.simplex.sh'  # API base URL
)
```

## API Reference

### SimplexClient

Main client class for interacting with the Simplex API.

**Methods:**
- `create_workflow_session(name, url, proxies=False, session_data=None)` - Create a new workflow session
- `get_session_store(session_id)` - Retrieve session store data
- `download_session_files(session_id, filename=None)` - Download files from a session
- `add_2fa_config(seed, name=None, partial_url=None)` - Add 2FA configuration
- `update_api_key(api_key)` - Update the API key
- `set_custom_header(key, value)` - Set a custom header
- `remove_custom_header(key)` - Remove a custom header

### Workflow Resource

Access via `client.workflows`

**Methods:**
- `run(workflow_id, variables=None, metadata=None, webhook_url=None)` - Execute a workflow
- `get_status(session_id)` - Get workflow execution status
- `create_workflow_session(workflow_name, url, proxies=False, session_data=None)` - Create a session
- `agentic(task, session_id, max_steps=None, actions_to_exclude=None, variables=None)` - Run agentic task
- `run_agent(agent_name, session_id, variables=None)` - Run a named agent
- `start_segment(workflow_id, segment_name)` - Start a workflow segment
- `finish_segment(workflow_id)` - Finish the current segment
- `start_capture(session_id)` - Start capture mode
- `stop_capture(session_id)` - Stop capture mode
- `close_workflow_session(session_id)` - Close a session

### WorkflowSession

Created via `client.create_workflow_session()`. Supports context manager protocol.

**Properties:**
- `session_id` - Unique session identifier
- `workflow_id` - Associated workflow ID
- `livestream_url` - URL to view live browser session
- `connect_url` - Connection URL
- `vnc_url` - VNC access URL
- `is_closed` - Whether the session is closed

**Methods:**
- `goto(url)` - Navigate to a URL
- `agentic(task, max_steps=None, actions_to_exclude=None, variables=None)` - Execute agentic task
- `run_agent(agent_name, variables=None)` - Run a named agent
- `start_capture()` - Start capture mode
- `stop_capture()` - Stop capture mode
- `close()` - Close the session

## Development

### Setup Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install simplex
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black simplex/
flake8 simplex/
mypy simplex/
```

## Examples

Check out the [examples](./examples) directory for more usage examples:

- `login_example.py` - Basic login workflow
- `create_workflow.py` - Creating and controlling sessions
- `run_workflow.py` - Running workflows with variables
- `download_file.py` - Downloading session files
- `add_2fa_config.py` - Adding 2FA configuration

## Requirements

- Python 3.8 or higher
- `requests>=2.25.0`
- `urllib3>=1.26.0`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://docs.simplex.sh](https://docs.simplex.sh)
- Email: support@simplex.sh
- GitHub Issues: [https://github.com/yourusername/simplex-python-sdk/issues](https://github.com/yourusername/simplex-python-sdk/issues)

## Changelog

### Version 1.0.0 (2024)

- Initial release
- Full feature parity with TypeScript SDK
- Support for workflow execution and session management
- Agentic task execution
- Named agent support
- File download capabilities
- 2FA configuration management
- Comprehensive error handling
- Type hints throughout
- Context manager support

---

Made with ❤️ by [Simplex](https://simplex.sh)