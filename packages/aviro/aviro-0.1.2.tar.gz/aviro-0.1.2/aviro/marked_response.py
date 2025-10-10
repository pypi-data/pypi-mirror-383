"""MarkedResponse class and auto_track_response function."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Span

from .utils import get_current_span


class MarkedResponse(str):
    """A string subclass that carries Tropir marker metadata and can self-mark.

    Usage:
        resp = await llm.ask(...)
        resp = resp.mark_response("marker_name")
        await llm.ask([{"role": "user", "content": resp}], stream=False)
    """

    def __new__(cls, text: str, marker_name: str = None):
        obj = str.__new__(cls, text)
        # Store optional marker name; will be set on mark_response if not provided
        obj.marker_name = marker_name
        return obj

    def mark_response(self, marker_name: str = None) -> 'MarkedResponse':
        """Mark this response on the current span and return self for chaining.

        This records the producing call id programmatically (no string matching).
        """
        span = get_current_span()
        if not span:
            return self

        name_to_use = marker_name or (self.marker_name or f"marked_{uuid.uuid4().hex[:8]}")
        self.marker_name = name_to_use

        # Use the most recent call id (the call that produced this response)
        from_call_id = None
        if getattr(span, "current_call_record", None):
            from_call_id = span.current_call_record.get("call_id")

        span.mark_response(name_to_use, str(self), from_call_id=from_call_id)
        return self


def auto_track_response(response_text: str) -> str:
    """
    Automatically track a response for flow detection without requiring MarkedResponse.

    This function allows ANY LLM abstraction to make their responses trackable by
    simply calling this function on the response text. The response will be automatically
    marked and tracked for flow detection in subsequent LLM calls.

    Args:
        response_text: The LLM response text to track

    Returns:
        The same response text (no modification, just tracking)

    Usage:
        # In any LLM abstraction:
        response = llm_api_call()
        return auto_track_response(response)  # Now trackable automatically
    """
    span = get_current_span()
    if not span or not response_text or not response_text.strip():
        return response_text

    # Create a synthetic call ID for manually tracked responses
    call_id = f"manual_{uuid.uuid4().hex[:8]}"

    # Auto-mark the response
    marker_name = span._auto_mark_response(response_text.strip(), call_id)
    if marker_name:
        # Add metadata about this manual tracking
        span.add(f"manual_track_{marker_name}", {
            "call_id": call_id,
            "content_length": len(response_text),
            "tracked_at": datetime.now().isoformat(),
            "tracking_method": "manual_auto_track"
        })

    return response_text

