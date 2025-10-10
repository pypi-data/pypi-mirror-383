"""
Aviro Span Module - Main entry point that re-exports all components.

This module maintains backward compatibility by importing and re-exporting
all classes and functions from the split modules.
"""

# Import exceptions
from .exceptions import (
    PromptNotFoundError,
    EvaluatorNotFoundError,
    PromptAlreadyExistsError,
    EvaluatorAlreadyExistsError,
)

# Import utilities
from .utils import (
    get_current_span,
    prompt,
    lm,
    _init_thread_local,
    _thread_local,
    _original_requests_session_send,
    _original_httpx_async_client_send,
)

# Import marked response
from .marked_response import (
    MarkedResponse,
    auto_track_response,
)

# Import core Span class
from .core import Span

# Import templates
from .templates import (
    PromptTemplate,
    EvaluatorTemplate,
)

# Import evaluator
from .evaluator import Evaluator

# Import wrappers
from .wrapper import (
    SpanLLMWrapper,
    SpanDecoratorContextManager,
)

# Import Tropir
from .tropir import Tropir

# Export all public APIs
__all__ = [
    # Exceptions
    "PromptNotFoundError",
    "EvaluatorNotFoundError",
    "PromptAlreadyExistsError",
    "EvaluatorAlreadyExistsError",
    # Core classes
    "Span",
    "Tropir",
    "PromptTemplate",
    "EvaluatorTemplate",
    "Evaluator",
    "MarkedResponse",
    "SpanLLMWrapper",
    "SpanDecoratorContextManager",
    # Utility functions
    "auto_track_response",
    "get_current_span",
    "prompt",
    "lm",
]
