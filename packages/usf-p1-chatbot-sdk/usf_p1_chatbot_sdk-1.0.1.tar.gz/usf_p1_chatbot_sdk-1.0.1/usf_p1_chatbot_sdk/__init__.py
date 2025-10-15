"""
USF P1 Chatbot SDK - Python Client for USF P1 Chatbot API

A lightweight Python SDK for interacting with the USF P1 Chatbot API.

Features:
- All 33 API endpoints wrapped
- Bearer token authentication
- Async streaming support
- Type hints and error handling
- Production-ready

Example:
    >>> from usf_p1_chatbot_sdk import ChatbotClient
    >>> 
    >>> client = ChatbotClient(
    ...     api_key="your-api-key-here",
    ...     base_url="https://your-api-endpoint.com"
    ... )
    >>> 
    >>> # Use any of 33 endpoints
    >>> collections = client.list_collections()
    >>> response = client.chat(
    ...     collection_id="col-123",
    ...     patient_user_name="John Doe",
    ...     message="Hello!"
    ... )
"""

__version__ = "1.0.1"
__author__ = "UltraSafe"
__email__ = "ravi.kumar@us.inc"

from .client import ChatbotClient, ChatbotClientError

__all__ = [
    "ChatbotClient",
    "ChatbotClientError",
    "__version__",
]
