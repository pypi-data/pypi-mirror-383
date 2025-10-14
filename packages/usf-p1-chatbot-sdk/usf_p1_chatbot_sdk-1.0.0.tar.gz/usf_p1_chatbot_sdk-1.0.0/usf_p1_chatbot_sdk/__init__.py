"""
USF P1 Chatbot SDK - Python Client for USF P1 Chatbot API

A lightweight Python SDK for interacting with the USF P1 Chatbot API.
Connect to the deployed API at https://api-civie.us.inc

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
    ...     api_key="your-api-key-here"
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

__version__ = "1.0.0"
__author__ = "UltraSafe"
__email__ = "support@ultrasafe.com"

from .client import ChatbotClient, ChatbotClientError

__all__ = [
    "ChatbotClient",
    "ChatbotClientError",
    "__version__",
]
