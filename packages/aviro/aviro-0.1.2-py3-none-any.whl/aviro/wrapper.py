import json
import time
import uuid
import threading
import requests
import httpx
import os
import hashlib
import re
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type
from contextlib import contextmanager
from urllib.parse import urlparse
import inspect
import weakref
import logging
from pydantic import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Span
    from .tropir import Tropir

from .marked_response import auto_track_response

class SpanDecoratorContextManager:
    """A class that can be used as both a decorator and context manager"""
    def __init__(self, tropir_instance: 'Tropir', span_name: str):
        self.tropir = tropir_instance
        self.span_name = span_name
        self._context_manager = None

    def __call__(self, func):
        """When used as decorator"""
        def wrapper(*args, **kwargs):
            with self.tropir._create_span(self.span_name) as span:
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        """When used as context manager"""
        self._context_manager = self.tropir._create_span(self.span_name)
        return self._context_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """When used as context manager"""
        if self._context_manager:
            return self._context_manager.__exit__(exc_type, exc_val, exc_tb)



class SpanLLMWrapper:
    """
    Universal LLM wrapper that automatically handles span tracking for ANY LLM abstraction.

    This wrapper automatically tracks responses from any method that returns text,
    without requiring specific method names or signatures. It works by:
    1. Intercepting method calls
    2. Automatically marking string responses for flow tracking
    3. Preserving the original API completely

    Compatible with any LLM abstraction - no changes needed to the underlying LLM.
    """

    def __init__(self, llm_instance, span: 'Span'):
        self.llm = llm_instance
        self.span = span

    def __getattr__(self, name):
        """
        Universal method interceptor that automatically tracks LLM responses.

        This intercepts ANY method call to the wrapped LLM and automatically
        tracks string responses without requiring specific method signatures.
        """
        attr = getattr(self.llm, name)

        # If it's not a callable, just return it
        if not callable(attr):
            return attr

        # Wrap the method to add automatic tracking
        if asyncio and inspect.iscoroutinefunction(attr):
            async def async_wrapper(*args, **kwargs):
                # Call the original method
                result = await attr(*args, **kwargs)

                # If the result is a string, automatically track it
                if isinstance(result, str) and result.strip():
                    # The HTTP interception already handles tracking, but for non-HTTP
                    # LLMs or local models, we can optionally track here
                    return auto_track_response(result)

                return result
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                # Call the original method
                result = attr(*args, **kwargs)

                # If the result is a string, automatically track it
                if isinstance(result, str) and result.strip():
                    # The HTTP interception already handles tracking, but for non-HTTP
                    # LLMs or local models, we can optionally track here
                    return auto_track_response(result)

                return result
            return sync_wrapper

