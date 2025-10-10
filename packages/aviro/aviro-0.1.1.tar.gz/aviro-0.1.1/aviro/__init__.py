"""
Aviro - A Python package for LLM execution tracking and flow analysis
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes/functions from span module
from .span import (
    Span,
    Tropir,
    PromptTemplate,
    EvaluatorTemplate,
    MarkedResponse,
    SpanLLMWrapper,
    auto_track_response,
    get_current_span,
    PromptNotFoundError,
    EvaluatorNotFoundError,
    PromptAlreadyExistsError,
    EvaluatorAlreadyExistsError,
)

__all__ = [
    "Span",
    "Tropir", 
    "PromptTemplate",
    "EvaluatorTemplate",
    "MarkedResponse",
    "SpanLLMWrapper",
    "auto_track_response",
    "get_current_span",
    "PromptNotFoundError",
    "EvaluatorNotFoundError", 
    "PromptAlreadyExistsError",
    "EvaluatorAlreadyExistsError",
]
