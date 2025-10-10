"""Utility functions and thread-local storage for Aviro package."""

import threading
import requests
import httpx
from typing import Optional

# Thread-local storage for patch management and prompt tracking
_thread_local = threading.local()

# Store original functions
_original_requests_session_send = requests.Session.send
_original_httpx_async_client_send = httpx.AsyncClient.send


def _init_thread_local():
    """Initialize thread-local storage if needed."""
    if not hasattr(_thread_local, 'patch_count'):
        _thread_local.patch_count = 0
    if not hasattr(_thread_local, 'httpx_patch_count'):
        _thread_local.httpx_patch_count = 0
    if not hasattr(_thread_local, 'pending_compiled_prompts'):
        _thread_local.pending_compiled_prompts = []
    if not hasattr(_thread_local, 'current_span_instance'):
        _thread_local.current_span_instance = None
    if not hasattr(_thread_local, 'original_messages_context'):
        _thread_local.original_messages_context = None
    if not hasattr(_thread_local, 'response_content_registry'):
        _thread_local.response_content_registry = {}  # content_hash -> marker_info


def get_current_span() -> Optional['Span']:
    """Get the current active span instance (if any)."""
    _init_thread_local()
    return getattr(_thread_local, 'current_span_instance', None)


def prompt(template: str) -> str:
    """Create a prompt string (legacy compatibility)"""
    return template


def lm():
    """Language model placeholder (legacy compatibility)"""
    pass

