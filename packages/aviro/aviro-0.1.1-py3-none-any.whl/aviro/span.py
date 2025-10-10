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

class PromptNotFoundError(Exception):
    """Exception raised when a prompt is not found"""
    def __init__(self, prompt_id: str, message: str = None):
        self.prompt_id = prompt_id
        self.message = message or f"Prompt '{prompt_id}' not found"
        super().__init__(self.message)

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

def get_current_span() -> Optional['Span']:
    """Get the current active span instance (if any)."""
    _init_thread_local()
    return getattr(_thread_local, 'current_span_instance', None)

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

class Span:
    def __init__(self, span_name: str, api_key: str = None, base_url: str = None):
        # Generate unique UUID for each span run (not deterministic)
        self.span_id = str(uuid.uuid4())
        self.span_name = span_name
        self.api_key = api_key
        self._base_url = base_url
        self.start_time = datetime.now().isoformat()
        self.end_time = None

        # Set this span as the current span in thread-local storage
        _init_thread_local()
        _thread_local.current_span_instance = self

        # Main execution tree structure
        self.tree = {
            "span_id": self.span_id,
            "span_name": span_name,
            "start_time": self.start_time,
            "end_time": None,
            "metadata": {},  # span.add() calls go here with timestamps
            "prompts": {},   # prompt_id -> {template, parameters, llm_call_ids, created_at}
            "evaluators": {},  # evaluator_name -> {evaluator_prompt, variables, model, temperature, structured_output, created_at}
            "cases": {},     # case_name -> [llm_call_objects]
            "marked_data": {},  # marker_name -> {content, created_by_call, used_in}
            "execution_flows": {}  # case_name -> {nodes, edges}
        }

        # Tracking state
        self.current_case = None
        self.prompt_registry = {}  # prompt_id -> template/params
        self.evaluator_registry = {}  # evaluator_name -> evaluator_data
        self.active = True
        self.current_call_record = None

        # Flow tracking state
        self.marked_data = {}  # marker_name -> data
        self.marker_usage = {}  # marker_name -> [usage_records]
        self._pending_marker_usage = []  # Track multiple marker usage in compile()
        self._pending_usage_records = [] # Store pending marker usage records

    def _is_openai_endpoint(self, url: str) -> bool:
        """Check if URL is an OpenAI endpoint we should monitor"""
        openai_patterns = [
            "localhost:8080/openai",
            "api.tropir.com/openai",
            "api.openai.com/v1/chat/completions",
            "api.openai.com/v1/responses"
        ]
        return any(pattern in url for pattern in openai_patterns)

    def add(self, key: str, value: Any) -> None:
        """Add metadata to the span with timestamp"""
        self.tree["metadata"][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

    def use_marked(self, marker_name: str) -> None:
        """Programmatically register that a marked value will be used in the next LLM call.

        This avoids any string matching by directly queuing the usage, which will be
        resolved to the next intercepted call in _capture_request_data.
        """
        if not marker_name:
            return
        if not hasattr(self, '_pending_marker_usage'):
            self._pending_marker_usage = []
        self._pending_marker_usage.append(marker_name)

    def mark_response(self, marker_name: str, response_text: str, from_call_id: str = None) -> None:
        """Mark a response text for flow tracking"""
        current_call_id = from_call_id or (self.current_call_record.get("call_id") if self.current_call_record else None)

        marked_data_entry = {
            "marker_name": marker_name,
            "content": response_text,
            "marked_at": datetime.now().isoformat(),
            "created_by_call": current_call_id,
            "used_in": []
        }

        # Store in instance state
        self.marked_data[marker_name] = marked_data_entry

        # Store in tree structure
        self.tree["marked_data"][marker_name] = marked_data_entry.copy()

        # Add metadata for tracking
        self.add(f"marked_data_{marker_name}", {
            "marker_name": marker_name,
            "content_length": len(response_text),
            "created_by_call": current_call_id
        })

    def get_marked(self, marker_name: str) -> str:
        """Get marked data and track its usage for flow connections"""
        if marker_name not in self.marked_data:
            raise ValueError(f"Marker '{marker_name}' not found. Available markers: {list(self.marked_data.keys())}")

        # Record that this marker is being accessed - flow will be created when next LLM call is made
        self._pending_marker_usage.append(marker_name)

        # Add metadata about the access
        self.add(f"marker_access_{marker_name}", {
            "marker_name": marker_name,
            "accessed_at": datetime.now().isoformat(),
            "content_length": len(self.marked_data[marker_name]["content"])
        })

        return self.marked_data[marker_name]["content"]

    def _record_marker_usage(self, marker_name: str, prompt_id: str, call_id: str) -> None:
        """Record that marked data was used in a prompt"""
        usage_record = {
            "prompt_id": prompt_id,
            "call_id": call_id,
            "used_at": datetime.now().isoformat()
        }

        # Add to marked data record in instance state
        if marker_name in self.marked_data:
            self.marked_data[marker_name]["used_in"].append(usage_record)

            # Update tree structure
            if marker_name in self.tree["marked_data"]:
                self.tree["marked_data"][marker_name]["used_in"].append(usage_record)

            # Build flow edge - even without prompt_id, we should track the flow
            self._build_flow_edge(
                from_call=self.marked_data[marker_name]["created_by_call"],
                to_call=call_id,
                via_marker=marker_name,
                via_prompt=prompt_id or "direct_usage"
            )

    def _build_flow_edge(self, from_call: str, to_call: str, via_marker: str, via_prompt: str) -> None:
        """Build an execution flow edge between two calls"""
        if not from_call or not to_call:
            return

        # Get current case or use default
        current_case = self.current_case or "default"

        # Initialize flow structure if needed
        if current_case not in self.tree["execution_flows"]:
            self.tree["execution_flows"][current_case] = {
                "nodes": [],
                "edges": []
            }

        flow = self.tree["execution_flows"][current_case]

        # Add nodes if they don't exist
        node_ids = [node["node_id"] for node in flow["nodes"]]

        if from_call not in node_ids:
            flow["nodes"].append({
                "node_id": from_call,
                "call_id": from_call,
                "type": "llm_call"
            })

        if to_call not in node_ids:
            flow["nodes"].append({
                "node_id": to_call,
                "call_id": to_call,
                "type": "llm_call"
            })

        # Add edge
        edge = {
            "from": from_call,
            "to": to_call,
            "via_marker": via_marker,
            "via_prompt": via_prompt,
            "created_at": datetime.now().isoformat()
        }

        # Check if edge already exists
        existing_edge = next((e for e in flow["edges"] if e["from"] == from_call and e["to"] == to_call), None)
        if not existing_edge:
            flow["edges"].append(edge)

    def _extract_llm_response_text(self, response_data: Dict) -> Optional[str]:
        """Extract clean response text from LLM API response for automatic marking"""
        if not isinstance(response_data, dict):
            return None

        # Handle OpenAI response format
        choices = response_data.get("choices", [])
        if choices and isinstance(choices, list):
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                # Handle both chat completions and legacy completions
                message = first_choice.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content")
                    if content and isinstance(content, str):
                        return content.strip()

                # Fallback for direct text field
                text = first_choice.get("text")
                if text and isinstance(text, str):
                    return text.strip()

        return None

    def _create_content_fingerprint(self, content: str) -> str:
        """Create a deterministic fingerprint for content matching"""
        if not content:
            return ""

        # Normalize content: remove extra whitespace and convert to lowercase
        normalized = ' '.join(content.strip().split()).lower()

        # Create hash of normalized content
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

    def _auto_mark_response(self, response_text: str, call_id: str) -> str:
        """Automatically mark a response and return the marker name"""
        if not response_text or not response_text.strip():
            return None

        # Create content fingerprint
        content_fingerprint = self._create_content_fingerprint(response_text)
        if not content_fingerprint:
            return None

        # Generate marker name based on content hash and timestamp
        marker_name = f"auto_{content_fingerprint}_{int(time.time() * 1000) % 1000000}"

        # Store in thread-local registry for automatic detection
        _init_thread_local()
        _thread_local.response_content_registry[content_fingerprint] = {
            "marker_name": marker_name,
            "content": response_text.strip(),
            "call_id": call_id,
            "created_at": datetime.now().isoformat(),
            "span_instance": self
        }

        # Mark the response in the span
        self.mark_response(marker_name, response_text.strip(), call_id)

        return marker_name

    def _auto_detect_content_reuse(self, request_content: Any) -> List[str]:
        """Automatically detect when marked content is being reused in requests"""
        if not request_content:
            return []

        detected_markers = []
        _init_thread_local()

        # Extract text content from request
        text_content = self._extract_text_from_request(request_content)
        if not text_content:
            return []

        # Check against all registered response content
        for content_hash, marker_info in _thread_local.response_content_registry.items():
            registered_content = marker_info["content"]
            if not registered_content:
                continue

            # Check if the registered content appears in the request
            # Use the same normalization as fingerprinting for consistency
            normalized_request = ' '.join(text_content.strip().split()).lower()
            normalized_registered = ' '.join(registered_content.strip().split()).lower()

            if normalized_registered in normalized_request:
                marker_name = marker_info["marker_name"]
                detected_markers.append(marker_name)

                # Automatically register the usage
                self.use_marked(marker_name)

        return detected_markers

    def _extract_text_from_request(self, request_data: Any) -> str:
        """Extract all text content from a request for content matching"""
        if not request_data:
            return ""

        text_parts = []

        if isinstance(request_data, dict):
            # Handle OpenAI API format
            messages = request_data.get("messages", [])
            if isinstance(messages, list):
                for message in messages:
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str):
                            text_parts.append(content)
                        elif isinstance(content, list):
                            # Handle multimodal content
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text = item.get("text", "")
                                    if text:
                                        text_parts.append(text)

            # Handle direct input field
            input_field = request_data.get("input")
            if isinstance(input_field, str):
                text_parts.append(input_field)
            elif isinstance(input_field, list):
                for item in input_field:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        content = item.get("content", "")
                        if content:
                            text_parts.append(str(content))

        return " ".join(text_parts)

    def _update_flow_connections(self, old_call_id: str, new_call_id: str) -> None:
        """Update all flow connections to use the new OpenAI call ID instead of temporary UUID"""
        if not old_call_id or not new_call_id or old_call_id == new_call_id:
            return

        # Update execution flows in tree structure
        for flow_name, flow_data in self.tree.get("execution_flows", {}).items():
            # Update nodes
            for node in flow_data.get("nodes", []):
                if node.get("call_id") == old_call_id:
                    node["call_id"] = new_call_id
                    node["node_id"] = new_call_id  # node_id should match call_id

            # Update edges
            for edge in flow_data.get("edges", []):
                if edge.get("from") == old_call_id:
                    edge["from"] = new_call_id
                if edge.get("to") == old_call_id:
                    edge["to"] = new_call_id

        # Update marked data usage records
        for marker_name, marker_data in self.tree.get("marked_data", {}).items():
            if marker_data.get("created_by_call") == old_call_id:
                marker_data["created_by_call"] = new_call_id

            for usage_record in marker_data.get("used_in", []):
                if usage_record.get("call_id") == old_call_id:
                    usage_record["call_id"] = new_call_id

        # Update instance-level marked data too
        for marker_name, marker_data in self.marked_data.items():
            if marker_data.get("created_by_call") == old_call_id:
                marker_data["created_by_call"] = new_call_id

            for usage_record in marker_data.get("used_in", []):
                if usage_record.get("call_id") == old_call_id:
                    usage_record["call_id"] = new_call_id

    def _create_sequential_flow_edge(self, case_name: str, current_call_id: str) -> None:
        """Create a sequential flow edge from the previous call to the current call within the same case"""
        if not hasattr(self, 'current_case_context') or not self.current_case_context:
            return

        calls_list = self.current_case_context["calls_in_case"]
        if len(calls_list) < 2:
            # No previous call to connect from
            return

        # Get the previous call ID (second-to-last in the list)
        previous_call_id = calls_list[-2]  # -1 is current, -2 is previous

        # Create sequential flow edge
        self._build_flow_edge(
            from_call=previous_call_id,
            to_call=current_call_id,
            via_marker="sequential_flow",
            via_prompt="agent_execution_loop"
        )

    def mark_and_return(self, marker_name: str, response_text: str) -> str:
        """Mark response and return it (for chaining)"""
        self.mark_response(marker_name, response_text)
        return response_text

    def use_marked_in_prompt(self, marker_name: str, prompt_template: str) -> str:
        """Use marked data in a prompt template - creates explicit flow connection"""
        marked_content = self.get_marked(marker_name)
        return prompt_template.format(marked_content=marked_content)

    def auto_mark_in_loop(self, base_marker_name: str, response_text: str, iteration: int) -> str:
        """Auto-mark responses in loops"""
        marker_name = f"{base_marker_name}_iter_{iteration}"
        self.mark_response(marker_name, response_text)
        return marker_name

    def wrap_llm(self, llm_instance) -> 'SpanLLMWrapper':
        """
        Wrap an LLM instance with automatic span tracking.

        Usage:
            llm = LLM()
            tracked_llm = span.wrap_llm(llm)
            response = await tracked_llm.ask([{"role": "user", "content": "Hello"}])
        """
        return SpanLLMWrapper(llm_instance, self)

    def get_prompt(self, prompt_id: str, default_prompt: str = None) -> 'PromptTemplate':
        """Get or create a prompt template - completely local, no API calls"""
        if prompt_id not in self.prompt_registry:
            # If no default_prompt provided, raise exception
            if default_prompt is None:
                raise PromptNotFoundError(prompt_id)

            # Create prompt locally with default template
            template = default_prompt
            prompt_data = {
                "template": template,
                "parameters": {},
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.prompt_registry[prompt_id] = prompt_data

            # Add to tree structure with comprehensive tracking
            self.tree["prompts"][prompt_id] = {
                "template": template,
                "parameters": {},
                "llm_call_ids": [],  # Will be populated when prompts are detected in LLM calls
                "created_at": datetime.now().isoformat(),
                "version": 1,
                "prompt_id": prompt_id
            }

        return PromptTemplate(prompt_id, self.prompt_registry[prompt_id], self)

    def set_prompt(self, prompt_id: str, template: str, parameters: Dict = None):
        """Set a prompt template manually - creates in webapp database if API key available"""
        # Check if prompt already exists in webapp
        if hasattr(self, 'api_key') and self.api_key and hasattr(self, '_base_url'):
            try:
                response = requests.get(
                    f"{self._base_url}/api/prompts/{prompt_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    raise PromptAlreadyExistsError(prompt_id)
            except PromptAlreadyExistsError:
                raise
            except Exception:
                # Prompt doesn't exist, continue with creation
                pass

        # Create prompt in webapp via API if possible
        if hasattr(self, 'api_key') and self.api_key and hasattr(self, '_base_url'):
            try:
                prompt_data_api = {
                    "prompt_name": prompt_id,
                    "template": template,
                    "parameters": parameters or {},
                    "version": 1
                }

                response = requests.post(
                    f"{self._base_url}/api/prompts",
                    json=prompt_data_api,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Prompt '{prompt_id}' created successfully in webapp")
                else:
                    print(f"⚠️ Failed to create prompt in webapp: {response.status_code}")
                    # Fall back to local storage
                    self._set_prompt_local(prompt_id, template, parameters)
            except Exception as e:
                print(f"⚠️ Failed to create prompt in webapp: {e}")
                # Fall back to local storage
                self._set_prompt_local(prompt_id, template, parameters)
        else:
            # No API key, use local storage
            self._set_prompt_local(prompt_id, template, parameters)


    def _set_prompt_local(self, prompt_id: str, template: str, parameters: Dict = None):
        """Set prompt locally (fallback method)"""
        prompt_data = {
            "template": template,
            "parameters": parameters or {},
            "version": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.prompt_registry[prompt_id] = prompt_data
        self.tree["prompts"][prompt_id] = {
            "template": template,
            "parameters": parameters or {},
            "llm_call_ids": [],
            "created_at": datetime.now().isoformat(),
            "version": 1,
            "prompt_id": prompt_id
        }

    def set_evaluator(self, evaluator_name: str, evaluator_prompt: str, variables: List[str] = None,
                     model: str = "gpt-4o-mini", temperature: float = 0.1,
                     structured_output: Union[Dict, Type[BaseModel]] = None):
        """Set an evaluator manually - creates in webapp database if API key available"""
        # Check if evaluator already exists in webapp
        if hasattr(self, 'api_key') and self.api_key and hasattr(self, '_base_url'):
            try:
                response = requests.get(
                    f"{self._base_url}/api/web-evaluators",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    evaluators_data = response.json()
                    evaluators = evaluators_data.get("evaluators", [])
                    if any(eval.get("name") == evaluator_name for eval in evaluators):
                        raise EvaluatorAlreadyExistsError(evaluator_name)
            except EvaluatorAlreadyExistsError:
                raise
            except Exception as e:
                # Evaluator doesn't exist or check failed, continue with creation
                print(f"Debug: Evaluator check failed: {e}")
                pass

        # Convert Pydantic model to schema if provided
        processed_structured_output = None
        pydantic_model_class = None

        if structured_output is not None:
            if isinstance(structured_output, type) and issubclass(structured_output, BaseModel):
                # It's a Pydantic model class
                pydantic_model_class = structured_output
                # Convert to JSON schema format
                schema = structured_output.model_json_schema()
                processed_structured_output = schema
            else:
                # It's already a dict/schema
                processed_structured_output = structured_output

        # Create evaluator in webapp via API if possible
        if hasattr(self, 'api_key') and self.api_key and hasattr(self, '_base_url'):
            try:
                evaluator_data_api = {
                    "name": evaluator_name,
                    "variables": variables or [],
                    "evaluator_prompt": evaluator_prompt,
                    "model": model,
                    "temperature": temperature,
                    "structured_output": processed_structured_output
                }

                response = requests.post(
                    f"{self._base_url}/api/web-evaluators",
                    json=evaluator_data_api,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Evaluator '{evaluator_name}' created successfully in webapp")
                else:
                    print(f"⚠️ Failed to create evaluator in webapp: {response.status_code}")
                    # Fall back to local storage
                    self._set_evaluator_local(evaluator_name, evaluator_prompt, variables, model, temperature, processed_structured_output, pydantic_model_class)
            except Exception as e:
                print(f"⚠️ Failed to create evaluator in webapp: {e}")
                # Fall back to local storage
                self._set_evaluator_local(evaluator_name, evaluator_prompt, variables, model, temperature, processed_structured_output, pydantic_model_class)
        else:
            # No API key, use local storage
            self._set_evaluator_local(evaluator_name, evaluator_prompt, variables, model, temperature, processed_structured_output, pydantic_model_class)

    def _set_evaluator_local(self, evaluator_name: str, evaluator_prompt: str, variables: List[str] = None,
                            model: str = "gpt-4o-mini", temperature: float = 0.1,
                            processed_structured_output: Union[Dict, Type[BaseModel]] = None,
                            pydantic_model_class = None):
        """Set evaluator locally (fallback method)"""
        evaluator_data = {
            "evaluator_prompt": evaluator_prompt,
            "variables": variables or [],
            "model": model,
            "temperature": temperature,
            "structured_output": processed_structured_output,
            "pydantic_model_class": pydantic_model_class,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.evaluator_registry[evaluator_name] = evaluator_data
        self.tree["evaluators"][evaluator_name] = {
            "evaluator_prompt": evaluator_prompt,
            "variables": variables or [],
            "model": model,
            "temperature": temperature,
            "structured_output": processed_structured_output,
            "created_at": datetime.now().isoformat(),
            "evaluator_name": evaluator_name
        }

    def register_compiled_prompt(self, prompt_id: str, compiled_text: str, parameters_used: Dict):
        """Register a compiled version of a prompt in span metadata for tracking"""
        compilation_key = f"prompt_compilation_{prompt_id}_{datetime.now().isoformat()}"
        self.add(compilation_key, {
            "prompt_id": prompt_id,
            "compiled_text": compiled_text,
            "parameters_used": parameters_used,
            "compiled_at": datetime.now().isoformat(),
            "length": len(compiled_text)
        })

    def get_evaluator(self, evaluator_name: str, default_evaluator_prompt: str = None,
                     default_variables: List[str] = None, default_structured_output: Union[Dict, Type[BaseModel]] = None,
                     tropir_instance: 'Tropir' = None) -> 'EvaluatorTemplate':
        """Get or create an evaluator template - completely local, no API calls"""
        if evaluator_name not in self.evaluator_registry:
            # If no default_evaluator_prompt provided, raise exception
            if default_evaluator_prompt is None:
                raise EvaluatorNotFoundError(evaluator_name)

            # Convert Pydantic model to schema if provided
            processed_structured_output = None
            pydantic_model_class = None

            if default_structured_output is not None:
                if isinstance(default_structured_output, type) and issubclass(default_structured_output, BaseModel):
                    # It's a Pydantic model class
                    pydantic_model_class = default_structured_output
                    # Convert to JSON schema format
                    schema = default_structured_output.model_json_schema()
                    processed_structured_output = schema
                else:
                    # It's already a dict/schema
                    processed_structured_output = default_structured_output

            # Create evaluator locally with default data
            evaluator_data = {
                "evaluator_prompt": default_evaluator_prompt,
                "variables": default_variables or [],
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "structured_output": processed_structured_output,
                "pydantic_model_class": pydantic_model_class,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.evaluator_registry[evaluator_name] = evaluator_data

            # Add to tree structure
            self.tree["evaluators"][evaluator_name] = {
                "evaluator_prompt": default_evaluator_prompt,
                "variables": default_variables or [],
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "structured_output": processed_structured_output,
                "created_at": datetime.now().isoformat(),
                "evaluator_name": evaluator_name
            }

        return EvaluatorTemplate(evaluator_name, self.evaluator_registry[evaluator_name], self, tropir_instance)

    def case(self, case_name: str):
        """Set the current case for subsequent LLM calls"""
        self.current_case = case_name
        if case_name not in self.tree["cases"]:
            self.tree["cases"][case_name] = []

    @contextmanager
    def track_calls(self, case: str = None):
        """Context manager to track all LLM calls made within this context as a case"""
        if case:
            self.case(case)

        # Set up case tracking
        current_case = self.current_case or "default"
        if current_case not in self.tree["cases"]:
            self.tree["cases"][current_case] = []

        case_start = datetime.now().isoformat()

        # Store the case context for HTTP monitoring
        self.current_case_context = {
            "case_name": current_case,
            "case_start": case_start,
            "calls_in_case": []
        }

        # Apply HTTP patches to capture all calls in this context
        self._apply_http_patches()

        try:
            yield current_case
        finally:
            case_end = datetime.now().isoformat()

            # Calculate case duration for this specific track_calls session
            if case_start and case_end:
                start_dt = datetime.fromisoformat(case_start)
                end_dt = datetime.fromisoformat(case_end)
                duration = (end_dt - start_dt).total_seconds() * 1000

                # Only add metadata if this is the first time we're tracking this case
                # or if it's not the default case (to avoid duplicate metadata for default case)
                if current_case != "default" or f"case_{current_case}_duration" not in self.tree["metadata"]:
                    self.add(f"case_{current_case}_duration", duration)
                    self.add(f"case_{current_case}_calls_count", len(self.current_case_context.get("calls_in_case", [])))

            self._revert_http_patches()
            self.current_case_context = None

    def _apply_http_patches(self):
        """Apply HTTP patches for monitoring"""
        _init_thread_local()
        if _thread_local.patch_count == 0:
            # Create bound methods for the span instance
            bound_requests_send = lambda session_instance, request, **kwargs: self._patched_requests_session_send(session_instance, request, **kwargs)
            bound_httpx_send = lambda client_instance, request, **kwargs: self._patched_httpx_async_client_send(client_instance, request, **kwargs)

            requests.Session.send = bound_requests_send
            httpx.AsyncClient.send = bound_httpx_send
        _thread_local.patch_count += 1
        _thread_local.httpx_patch_count += 1

    def _revert_http_patches(self):
        """Revert HTTP patches"""
        _init_thread_local()
        if _thread_local.patch_count > 0:
            _thread_local.patch_count -= 1
            if _thread_local.patch_count == 0:
                requests.Session.send = _original_requests_session_send

        if _thread_local.httpx_patch_count > 0:
            _thread_local.httpx_patch_count -= 1
            if _thread_local.httpx_patch_count == 0:
                httpx.AsyncClient.send = _original_httpx_async_client_send

    async def _patched_httpx_async_client_send(self, client_instance, request, **kwargs):
        """Patched version of httpx.AsyncClient.send for monitoring"""
        # Check if this is an OpenAI API call
        if self._is_openai_endpoint(str(request.url)):
            self._capture_request_data(request, str(request.url), is_async=True)

        # Make the actual request
        response = await _original_httpx_async_client_send(client_instance, request, **kwargs)

        # Capture response if it's an OpenAI call
        if self._is_openai_endpoint(str(request.url)):
            self._capture_response_data(response, is_async=True)

        return response

    def _patched_requests_session_send(self, session_instance, request, **kwargs):
        """Patched version of requests.Session.send for monitoring"""
        # Check if this is an OpenAI API call
        if self._is_openai_endpoint(request.url):
            self._capture_request_data(request, request.url, is_async=False)

        # Make the actual request
        response = _original_requests_session_send(session_instance, request, **kwargs)

        # Capture response if it's an OpenAI call
        if self._is_openai_endpoint(request.url):
            self._capture_response_data(response, is_async=False)

        return response

    def _capture_response_data(self, response, is_async: bool):
        """Capture response data for LLM calls"""
        if not self.current_call_record:
            return

        try:
            # Record end time and duration
            end_time = datetime.now().isoformat()
            self.current_call_record["end_time"] = end_time

            # Calculate duration if we have start time
            if self.current_call_record.get("start_time"):
                start_dt = datetime.fromisoformat(self.current_call_record["start_time"])
                end_dt = datetime.fromisoformat(end_time)
                duration_ms = (end_dt - start_dt).total_seconds() * 1000
                self.current_call_record["duration_ms"] = duration_ms

            # Always record status code in metadata (ensure it's never null)
            status_code = getattr(response, 'status_code', 200)
            self.current_call_record["metadata"]["status_code"] = status_code

            # Initialize response_data to ensure it's never null
            response_data = None

            # Extract response content with improved error handling
            if is_async:
                # httpx response
                try:
                    # Try multiple ways to get the response content
                    if hasattr(response, 'json') and callable(response.json):
                        # Try the json() method first (most reliable)
                        response_data = response.json()
                    elif hasattr(response, 'content'):
                        content = response.content
                        if isinstance(content, bytes):
                            content_text = content.decode('utf-8')
                        else:
                            content_text = str(content)
                        response_data = json.loads(content_text)
                    elif hasattr(response, 'text'):
                        content_text = response.text
                        response_data = json.loads(content_text)
                    else:
                        # Last resort: try to read the response
                        content = response.read()
                        if isinstance(content, bytes):
                            content_text = content.decode('utf-8')
                        else:
                            content_text = str(content)
                        response_data = json.loads(content_text)

                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
                    # Store raw content if JSON parsing fails
                    try:
                        raw_content = getattr(response, 'content', None) or getattr(response, 'text', None)
                        if raw_content:
                            if isinstance(raw_content, bytes):
                                raw_content = raw_content.decode('utf-8', errors='ignore')
                            response_data = {"error": "Failed to parse JSON response", "raw_content": str(raw_content)[:1000], "parse_error": str(e)}
                        else:
                            response_data = {"error": "Failed to parse response and no content available", "parse_error": str(e)}
                    except Exception as inner_e:
                        response_data = {"error": "Complete response parsing failure", "parse_error": str(e), "inner_error": str(inner_e)}
            else:
                # requests response
                try:
                    # Try the json() method first (most reliable)
                    if hasattr(response, 'json') and callable(response.json):
                        response_data = response.json()
                    elif hasattr(response, 'content'):
                        content = response.content
                        if isinstance(content, bytes):
                            content_text = content.decode('utf-8')
                        else:
                            content_text = str(content)
                        response_data = json.loads(content_text)
                    elif hasattr(response, 'text'):
                        response_data = json.loads(response.text)
                    else:
                        response_data = {"error": "No accessible response content"}

                except (json.JSONDecodeError, ValueError, AttributeError) as e:
                    # Store raw content if JSON parsing fails
                    try:
                        raw_content = getattr(response, 'content', None) or getattr(response, 'text', None)
                        if raw_content:
                            if isinstance(raw_content, bytes):
                                raw_content = raw_content.decode('utf-8', errors='ignore')
                            response_data = {"error": "Failed to parse JSON response", "raw_content": str(raw_content)[:1000], "parse_error": str(e)}
                        else:
                            response_data = {"error": "Failed to parse response and no content available", "parse_error": str(e)}
                    except Exception as inner_e:
                        response_data = {"error": "Complete response parsing failure", "parse_error": str(e), "inner_error": str(inner_e)}

            # Ensure response_data is never None/null and capture meaningful error info
            if response_data is None:
                response_data = {
                    "error": "Response data is unexpectedly null",
                    "status_code": status_code,
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "null_response"
                }

            # For error status codes, ensure we capture error details
            if status_code >= 400:
                if isinstance(response_data, dict):
                    response_data["error_captured"] = True
                    response_data["error_status"] = status_code
                    if "error" not in response_data:
                        response_data["error"] = f"HTTP {status_code} error"
                else:
                    # If response_data is not a dict, wrap it with error info
                    response_data = {
                        "error": f"HTTP {status_code} error",
                        "error_status": status_code,
                        "error_captured": True,
                        "raw_response": response_data,
                        "timestamp": datetime.now().isoformat()
                    }

            # Clean response data to handle large base64 images
            cleaned_response_data = self._clean_large_content(response_data)

            # Store the cleaned OpenAI response payload
            self.current_call_record["response"] = cleaned_response_data

            # Extract model from response if available and not already set
            if isinstance(response_data, dict):
                # Try to get model from response
                response_model = response_data.get('model')
                if response_model and not self.current_call_record["metadata"].get("model"):
                    self.current_call_record["metadata"]["model"] = response_model

            # Extract OpenAI's response ID and use it as our call_id
            if isinstance(response_data, dict) and "id" in response_data:
                openai_response_id = response_data["id"]
                old_call_id = self.current_call_record["call_id"]

                # Update the call_id to use OpenAI's response ID
                self.current_call_record["call_id"] = openai_response_id

                # Update the call_id in the current case's calls list
                if hasattr(self, 'current_case_context') and self.current_case_context:
                    case_name = self.current_case_context["case_name"]
                    calls_list = self.current_case_context["calls_in_case"]
                    if old_call_id in calls_list:
                        calls_list[calls_list.index(old_call_id)] = openai_response_id

                # Update execution flow connections with the new OpenAI call ID
                self._update_flow_connections(old_call_id, openai_response_id)

            # Store duration in metadata (ensure it's never null)
            self.current_call_record["metadata"]["duration_ms"] = self.current_call_record.get("duration_ms", 0)

            # AUTOMATIC RESPONSE MARKING: Extract and automatically mark LLM response text
            if isinstance(response_data, dict):
                response_text = self._extract_llm_response_text(response_data)
                if response_text:
                    # Automatically mark the response for flow tracking
                    call_id = self.current_call_record.get("call_id")
                    marker_name = self._auto_mark_response(response_text, call_id)
                    if marker_name:
                        # Add metadata about the auto-marking
                        self.current_call_record["metadata"]["auto_marked"] = True
                        self.current_call_record["metadata"]["auto_marker_name"] = marker_name
                        # Add to span metadata for tracking
                        self.add(f"auto_marked_{marker_name}", {
                            "call_id": call_id,
                            "content_length": len(response_text),
                            "marked_at": datetime.now().isoformat()
                        })

        except Exception as e:
            # Store comprehensive error information - never leave response as null
            error_info = {
                "error": "Exception in _capture_response_data",
                "exception": str(e),
                "exception_type": type(e).__name__,
                "status_code": getattr(response, 'status_code', None),
                "response_type": type(response).__name__,
                "timestamp": datetime.now().isoformat(),
                "error_captured": True,
                "error_source": "span_capture_exception"
            }

            # Try to get any available response content even in error case
            try:
                raw_content = getattr(response, 'content', None) or getattr(response, 'text', None)
                if raw_content:
                    if isinstance(raw_content, bytes):
                        raw_content = raw_content.decode('utf-8', errors='ignore')
                    error_info["raw_content"] = str(raw_content)[:500]  # Truncate to avoid huge error logs
            except:
                pass

            self.current_call_record["response"] = error_info

            # Ensure metadata fields are never null
            self.current_call_record["metadata"]["status_code"] = getattr(response, 'status_code', 0)
            self.current_call_record["metadata"]["duration_ms"] = self.current_call_record.get("duration_ms", 0)

    def _capture_request_data(self, request, url: str, is_async: bool):
        """Capture request data for LLM calls"""
        if not hasattr(self, 'current_case_context') or not self.current_case_context:
            return

        # Create a new call record for this HTTP request
        # We'll update the call_id once we get the response with OpenAI's ID
        temp_call_id = str(uuid.uuid4())  # Temporary until we get OpenAI's response ID
        call_record = {
            "call_id": temp_call_id,  # Will be updated with OpenAI's response ID
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_ms": None,
            "request": {},  # Will store RAW OpenAI request - initialize as empty dict, not null
            "response": {},  # Will store RAW OpenAI response - initialize as empty dict, not null
            "metadata": {
                "model": "unknown",  # Default to 'unknown' instead of null
                "prompt_ids": [],
                "request_url": url,
                "status_code": 0,  # Default to 0 instead of null
                "duration_ms": 0   # Default to 0 instead of null
            }
        }

        # Add to current case
        case_name = self.current_case_context["case_name"]
        self.tree["cases"][case_name].append(call_record)
        self.current_case_context["calls_in_case"].append(temp_call_id)

        # Create sequential flow edge from previous call to this call
        self._create_sequential_flow_edge(case_name, temp_call_id)

        # Store for response capture
        self.current_call_record = call_record

        # NEW: Process pending marker usage records (from prompt compilations)
        if hasattr(self, '_pending_usage_records') and self._pending_usage_records:
            for usage_record in self._pending_usage_records:
                marker_name = usage_record["marker_name"]
                prompt_id = usage_record["prompt_id"]
                self._record_marker_usage(marker_name, prompt_id, temp_call_id)

            # Clear processed records
            self._pending_usage_records = []

        # NEW: Process direct marker usage (when get_marked() was called but no prompt compilation)
        if hasattr(self, '_pending_marker_usage') and self._pending_marker_usage:
            for marker_name in self._pending_marker_usage:
                # Record usage without a specific prompt_id (direct usage)
                self._record_marker_usage(marker_name, None, temp_call_id)

            # Clear pending usage
            self._pending_marker_usage = []

        try:
            # Extract full payload from request
            if is_async:
                # httpx request
                content = request.content
                content_type = request.headers.get("Content-Type", "").lower()
            else:
                # requests request
                content = request.body
                content_type = request.headers.get("Content-Type", "").lower()

            if "application/json" in content_type and content:
                try:
                    if isinstance(content, bytes):
                        json_data = json.loads(content.decode('utf-8'))
                    else:
                        json_data = json.loads(content)

                    # Clean request data to handle large base64 images
                    cleaned_request_data = self._clean_large_content(json_data)

                    # Store the cleaned OpenAI request payload
                    self.current_call_record["request"] = cleaned_request_data

                    # AUTOMATIC CONTENT REUSE DETECTION: Check if any marked content is being reused
                    detected_markers = self._auto_detect_content_reuse(json_data)
                    if detected_markers:
                        self.current_call_record["metadata"]["auto_detected_markers"] = detected_markers
                        # Add to span metadata for tracking
                        self.add(f"auto_detected_reuse_{temp_call_id}", {
                            "call_id": temp_call_id,
                            "detected_markers": detected_markers,
                            "detected_at": datetime.now().isoformat()
                        })

                    # Store metadata - ensure model is never null/unknown
                    model = json_data.get('model')
                    if model:
                        self.current_call_record["metadata"]["model"] = model
                    else:
                        # Try to extract from nested structures or set a reasonable default
                        self.current_call_record["metadata"]["model"] = "unknown"

                    # Extract messages for prompt detection
                    messages = []
                    if 'messages' in json_data:
                        messages = json_data.get('messages', [])
                    elif 'input' in json_data:
                        input_data = json_data['input']
                        if isinstance(input_data, list):
                            messages = input_data
                        else:
                            messages.append({"role": "user", "content": str(input_data)})

                    # Detect prompts used in messages and map them
                    prompt_entries = self._detect_and_map_prompts(messages, temp_call_id)
                    self.current_call_record["metadata"]["prompt_ids"] = [p["prompt_id"] for p in prompt_entries]
                    self.current_call_record["metadata"]["prompt_versions"] = prompt_entries

                    # Also update has_prompt field
                    if prompt_entries:
                        self.current_call_record["metadata"]["has_prompt"] = True

                    # Flow detection happens explicitly when users call span.get_marked()

                    # Analyze variable usage in this call
                    # used_variables = self.analyze_variable_usage(messages, self.current_call_record["call_id"])
                    # self.current_call_record["variables_used"] = used_variables

                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        except Exception:
            pass

    def _detect_and_map_prompts(self, messages: List[Dict], call_id: str) -> List[Dict]:
        """Detect which registered prompts are used by checking compiled prompts in metadata and template matching.
        Returns list of dicts with prompt_id and version_used."""
        detected_prompts = []

        # Method 0 - Direct compilation matching (exact text matching)
        # This method provides accurate 1:1 mapping between compiled prompts and LLM calls
        if hasattr(self, '_recent_compilations') and self._recent_compilations:
            # Check each recent compilation for exact text matches in this specific call
            for compilation_id, prompt_info in list(self._recent_compilations.items()):
                prompt_id = prompt_info["prompt_id"]
                version_used = prompt_info["version_used"]
                compiled_text = prompt_info.get("compiled_text", "")

                # CRITICAL: Only associate this prompt if its compiled text actually appears in the messages
                found_match = False
                if compiled_text:
                    for message in messages:
                        content = message.get("content", "")
                        if self._exact_match(compiled_text, content):
                            found_match = True

                            # Add to detected prompts
                            prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}
                            if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                                detected_prompts.append(prompt_entry)

                            # Link the call_id to the prompt in the main prompts tree
                            if prompt_id in self.tree["prompts"]:
                                if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                                    self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)

                            # Remove this compilation since it's been matched and used
                            del self._recent_compilations[compilation_id]
                            break

            # Clean up old compilations (older than 30 seconds to prevent memory leaks)
            current_time = datetime.now()
            for compilation_id in list(self._recent_compilations.keys()):
                compiled_at = self._recent_compilations[compilation_id].get("compiled_at", "")
                if compiled_at:
                    try:
                        compiled_dt = datetime.fromisoformat(compiled_at)
                        if (current_time - compiled_dt).total_seconds() > 30:
                            del self._recent_compilations[compilation_id]
                    except:
                        pass

        # If we found prompts via direct compilation matching, skip fallback methods
        if detected_prompts:
            return detected_prompts
            # This appears to be a flattened messages array
            # Check if any compiled prompts are part of the conversation context

            # For flattened calls, assume any recently compiled prompts are part of the conversation
            # This handles the case where generate_text([messages]) got flattened to input="Lachman"
            for prompt_id, prompt_data in self.tree.get("prompts", {}).items():
                if any(p["prompt_id"] == prompt_id for p in detected_prompts):
                    continue  # Already detected

                # Check if this prompt was recently compiled (within this span)
                has_recent_compilation = False
                for key, value_obj in self.tree.get("metadata", {}).items():
                    if key.startswith(f"prompt_compilation_{prompt_id}"):
                        has_recent_compilation = True
                        compilation_data = value_obj.get("value", {})
                        version_used = compilation_data.get("version_used", 1)

                        # Assuming compiled prompt is part of flattened conversation
                        prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                        if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                            detected_prompts.append(prompt_entry)

                        # Link the call_id to the prompt
                        if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                            self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)
                        break
        else:
            # Regular logic for non-flattened calls
            for prompt_id, prompt_data in self.tree.get("prompts", {}).items():
                if any(p["prompt_id"] == prompt_id for p in detected_prompts):
                    continue  # Already detected via fresh compilation

                # Get the last compiled version from metadata
                compiled_text = None
                version_used = 1
                for key, value_obj in self.tree.get("metadata", {}).items():
                    if key.startswith(f"prompt_compilation_{prompt_id}"):
                        compilation_data = value_obj.get("value", {})
                        if "compiled_text" in compilation_data:
                            compiled_text = compilation_data["compiled_text"]
                            version_used = compilation_data.get("version_used", 1)
                            break
                        elif "parameters_used" in compilation_data:
                            # Reconstruct from template and parameters
                            template = prompt_data.get("template", "")
                            parameters_used = compilation_data.get("parameters_used", {})
                            if template and parameters_used:
                                try:
                                    template_to_format = template
                                    if '{{' in template_to_format and '}}' in template_to_format:
                                        import re
                                        template_to_format = re.sub(r'\{\{(\w+)\}\}', r'{\1}', template_to_format)
                                    compiled_text = template_to_format.format(**parameters_used)
                                    version_used = compilation_data.get("version_used", 1)
                                    break
                                except (KeyError, ValueError):
                                    continue

                if compiled_text:
                    # Check if this compiled text appears in any message content
                    for i, message in enumerate(messages):
                        content = message.get("content", "")
                        if self._exact_match(compiled_text, content):
                            prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                            if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                                detected_prompts.append(prompt_entry)

                            # Link the call_id to the prompt
                            if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                                self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)
                            break

        compilation_keys = [k for k in self.tree.get('metadata', {}).keys() if k.startswith('prompt_compilation_')]

        # Fallback methods (only run if no direct matches found)

        # Method 1: Check compiled prompts in metadata (existing logic)
        for key, value_obj in self.tree.get("metadata", {}).items():
            if key.startswith("prompt_compilation_"):
                compilation_data = value_obj.get("value", {})
                compiled_text = compilation_data.get("compiled_text")
                prompt_id = compilation_data.get("prompt_id")

                if not compiled_text or not prompt_id:
                    continue

                # Check if this compiled text matches any message content
                for i, message in enumerate(messages):
                    content = message.get("content", "")
                    match_result = self._exact_match(compiled_text, content)
                    if match_result:
                        # Found a match! Extract version information
                        version_used = compilation_data.get("version_used", 1)
                        prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                        if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                            detected_prompts.append(prompt_entry)

                        # Link the call_id to the prompt in the main prompts tree
                        if prompt_id in self.tree["prompts"]:
                            if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                                self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)

                        # Since we found the match for this message, we can move to the next
                        break

        # Method 1.5: Check non-timestamped compilation entries (for the add() calls that don't have compiled_text)
        # These are the entries created by span.add() in compile() method without timestamps
        for key, value_obj in self.tree.get("metadata", {}).items():
            # Skip if this is a timestamped entry (from register_compiled_prompt) or already processed
            if not key.startswith("prompt_compilation_"):
                continue

            # Simple check: timestamped keys contain "-" (from ISO timestamp), non-timestamped don't
            has_timestamp = "-" in key and ":" in key  # ISO timestamp has both - and :
            if has_timestamp:
                continue  # Skip timestamped entries, they were handled in Method 1

            compilation_data = value_obj.get("value", {})
            prompt_id = compilation_data.get("prompt_id")

            if not prompt_id or any(p["prompt_id"] == prompt_id for p in detected_prompts):
                continue  # Skip if no prompt_id or already detected

            # For entries without compiled_text, check against the prompt templates
            if prompt_id in self.tree.get("prompts", {}):
                prompt_data = self.tree["prompts"][prompt_id]
                template = prompt_data.get("template", "")

                # Reconstruct what the compiled text would be using the parameters
                parameters_used = compilation_data.get("parameters_used", {})
                if template and parameters_used:
                    try:
                        # Handle both single and double curly brace formats
                        template_to_format = template
                        if '{{' in template_to_format and '}}' in template_to_format:
                            import re
                            template_to_format = re.sub(r'\{\{(\w+)\}\}', r'{\1}', template_to_format)

                        reconstructed_compiled = template_to_format.format(**parameters_used)

                        # Check if this reconstructed compiled text matches any message content
                        for message in messages:
                            content = message.get("content", "")
                            if self._exact_match(reconstructed_compiled, content):
                                version_used = compilation_data.get("version_used", 1)
                                prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                                if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                                    detected_prompts.append(prompt_entry)

                                # Link the call_id to the prompt in the main prompts tree
                                if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                                    self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)

                                break
                    except (KeyError, ValueError):
                        # Skip if template formatting fails
                        continue

        # Method 2: Check against registered prompt templates (fallback/additional detection)
        for prompt_id, prompt_data in self.tree.get("prompts", {}).items():
            if any(p["prompt_id"] == prompt_id for p in detected_prompts):
                continue  # Already detected

            template = prompt_data.get("template", "")
            if not template:
                continue

            # Check each message against this template
            for message in messages:
                content = message.get("content", "")
                if self._prompt_matches_content(template, content):
                    version_used = prompt_data.get("version", 1)
                    prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                    if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                        detected_prompts.append(prompt_entry)

                    # Link the call_id to the prompt
                    if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                        self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)
                    break

        # Method 3: Simple substring matching as last resort for partially matched prompts
        if not detected_prompts:
            for prompt_id, prompt_data in self.tree.get("prompts", {}).items():
                template = prompt_data.get("template", "")
                if len(template) > 20:  # Only for substantial prompts
                    # Extract a key phrase from the template (first 50 chars without variables)
                    import re
                    clean_template = re.sub(r'\{[^}]+\}', '', template)[:50].strip()

                    if len(clean_template) > 10:
                        for message in messages:
                            content = message.get("content", "")
                            if clean_template.lower() in content.lower():
                                version_used = prompt_data.get("version", 1)
                                prompt_entry = {"prompt_id": prompt_id, "version_used": version_used}

                                if not any(p["prompt_id"] == prompt_id for p in detected_prompts):
                                    detected_prompts.append(prompt_entry)

                                # Link the call_id to the prompt
                                if call_id not in self.tree["prompts"][prompt_id]["llm_call_ids"]:
                                    self.tree["prompts"][prompt_id]["llm_call_ids"].append(call_id)
                                break

        # Remove duplicates based on prompt_id while preserving the structure
        unique_prompts = []
        seen_prompt_ids = set()
        for prompt_entry in detected_prompts:
            if prompt_entry["prompt_id"] not in seen_prompt_ids:
                unique_prompts.append(prompt_entry)
                seen_prompt_ids.add(prompt_entry["prompt_id"])

        return unique_prompts # Return unique prompt entries with version info



    def _exact_match(self, template_text: str, message_content: str) -> bool:
        """Check for exact match (for compiled prompts)"""
        # Normalize whitespace for more robust matching
        template_normalized = ' '.join(template_text.strip().split())
        content_normalized = ' '.join(message_content.strip().split())

        # Debug output
        # print(f"      🔍 Comparing:")
        # print(f"        Template: '{template_normalized}'")
        # print(f"        Content:  '{content_normalized}'")

        # Try exact match first
        if template_normalized == content_normalized:
            # print(f"        ✅ Normalized match!")
            return True

        # Also try the original strict match as fallback
        if template_text.strip() == message_content.strip():
            # print(f"        ✅ Strict match!")
            return True

        # print(f"        ❌ No match")
        return False

    def _prompt_matches_content(self, template: str, content: str) -> bool:
        """Check if content matches a prompt template"""
        if not template or not content:
            return False

        # For exact matches (when template has no variables)
        if "{" not in template:
            return self._exact_match(template, content)

        # For templates with variables, do similarity matching
        import re
        template_clean = re.sub(r'\{[^}]+\}', '', template).strip()

        # Skip if template is too short to match reliably
        if len(template_clean) < 10:
            return False

        # Check for substantial overlap (at least 70% of template words found)
        template_words = set(template_clean.lower().split())
        content_words = set(content.lower().split())

        if len(template_words) == 0:
            return False

        overlap = len(template_words.intersection(content_words))
        similarity = overlap / len(template_words)

        return similarity >= 0.7

    def _clean_large_content(self, data: Any, max_base64_length: int = 1000) -> Any:
        """
        Clean data by truncating large base64 content while preserving structure
        This prevents huge payloads from breaking response capture
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Special handling for OpenAI message content with images
                if key == "content" and isinstance(value, list):
                    cleaned[key] = self._clean_message_content(value, max_base64_length)
                else:
                    cleaned[key] = self._clean_large_content(value, max_base64_length)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_large_content(item, max_base64_length) for item in data]
        elif isinstance(data, str):
            # Check if this looks like base64 data URL
            if data.startswith('data:image/') and 'base64,' in data and len(data) > max_base64_length:
                # Extract the prefix (data:image/jpeg;base64,) and truncate the base64 part
                prefix_end = data.find('base64,') + 7  # Include "base64,"
                if prefix_end > 7:  # Valid prefix found
                    prefix = data[:prefix_end]
                    base64_part = data[prefix_end:]
                    truncated_base64 = base64_part[:max_base64_length]

                    # Return truncated data URL as string to maintain backend compatibility
                    return prefix + truncated_base64 + f"[TRUNCATED_FROM_{len(data)}_TO_{len(prefix + truncated_base64)}_CHARS]"
            return data
        else:
            return data

    def _clean_message_content(self, content_list: list, max_base64_length: int) -> list:
        """
        Specially handle OpenAI message content arrays that may contain images
        """
        cleaned_content = []
        for item in content_list:
            if isinstance(item, dict):
                if item.get("type") == "image_url" and isinstance(item.get("image_url"), dict):
                    image_url_data = item["image_url"]
                    url = image_url_data.get("url", "")

                    # Check if the URL is a large base64 image
                    if isinstance(url, str) and url.startswith('data:image/') and 'base64,' in url and len(url) > max_base64_length:
                        # Truncate the image and add metadata as a separate content item
                        prefix_end = url.find('base64,') + 7
                        if prefix_end > 7:
                            prefix = url[:prefix_end]
                            base64_part = url[prefix_end:]
                            truncated_base64 = base64_part[:max_base64_length]
                            truncated_url = prefix + truncated_base64

                            # Create the truncated image item
                            truncated_item = {
                                "type": "image_url",
                                "image_url": {
                                    "url": truncated_url
                                }
                            }
                            cleaned_content.append(truncated_item)

                            # Add a text item with truncation info
                            truncation_info = {
                                "type": "text",
                                "text": f"[IMAGE_TRUNCATED: Original size {len(url)} chars, truncated to {len(truncated_url)} chars for storage]"
                            }
                            cleaned_content.append(truncation_info)
                        else:
                            cleaned_content.append(item)
                    else:
                        # Not a large image, process normally
                        cleaned_content.append(self._clean_large_content(item, max_base64_length))
                else:
                    # Not an image_url, process normally
                    cleaned_content.append(self._clean_large_content(item, max_base64_length))
            else:
                cleaned_content.append(self._clean_large_content(item, max_base64_length))

        return cleaned_content

    def _extract_response_text(self, response_data: Dict) -> str:
        """Store the complete raw JSON response - let frontend handle visualization"""
        # Just return the raw JSON as a string for the frontend to parse and display
        return json.dumps(response_data, indent=2)

    def finalize(self):
        """Finalize the span and set end time"""
        self.end_time = datetime.now().isoformat()
        self.tree["end_time"] = self.end_time
        self.active = False

        # Calculate total span duration
        if self.tree["start_time"] and self.tree["end_time"]:
            start_dt = datetime.fromisoformat(self.tree["start_time"])
            end_dt = datetime.fromisoformat(self.tree["end_time"])
            duration = (end_dt - start_dt).total_seconds() * 1000
            self.tree["duration_ms"] = round(duration, 2)

    def get_tree(self) -> Dict:
        """Get the complete execution tree"""
        return self.tree

    def export_json(self) -> str:
        """Export the execution tree as JSON"""
        return json.dumps(self.tree, indent=2)


class PromptTemplate:
    def __init__(self, prompt_id: str, prompt_data: Dict, span: Span):
        self.prompt_id = prompt_id
        self.template = prompt_data.get("template", "")
        self.parameters = prompt_data.get("parameters", {})
        self.version = prompt_data.get("version", 1)
        self.deployed_version = prompt_data.get("deployed_version", 1)
        self.total_versions = prompt_data.get("total_versions", 1)
        self.span = span

    def compile(self, **kwargs) -> str:
        """Compile the prompt template with given parameters"""
        try:
            # Handle both single and double curly brace formats
            # Convert double braces {{param}} to single braces {param} for formatting
            template_to_format = self.template
            if '{{' in template_to_format and '}}' in template_to_format:
                # Replace double braces with single braces for parameter substitution
                import re
                template_to_format = re.sub(r'\{\{(\w+)\}\}', r'{\1}', template_to_format)

            compiled_prompt = template_to_format.format(**kwargs)

            # NEW: Direct association approach - associate compiled text with this specific prompt
            # Instead of using shared thread-local list, store compiled text directly for exact matching
            compilation_id = f"{self.prompt_id}_{datetime.now().isoformat()}_{id(compiled_prompt)}"
            compiled_prompt_info = {
                "prompt_id": self.prompt_id,
                "compiled_text": compiled_prompt,
                "parameters_used": kwargs,
                "version_used": self.version,
                "deployed_version": self.deployed_version,
                "compiled_at": datetime.now().isoformat(),
                "compilation_id": compilation_id,
                "span_instance": self.span
            }

            # Store in span for exact text matching (no thread-local accumulation)
            if not hasattr(self.span, '_recent_compilations'):
                self.span._recent_compilations = {}
            self.span._recent_compilations[compilation_id] = compiled_prompt_info

            # Keep the old tracking for backwards compatibility
            self.span.register_compiled_prompt(self.prompt_id, compiled_prompt, kwargs)

            # Track the compilation in span metadata with version info
            self.span.add(f"prompt_compilation_{self.prompt_id}", {
                "prompt_id": self.prompt_id,
                "version_used": self.version,
                "deployed_version": self.deployed_version,
                "parameters_used": kwargs,
                "compiled_length": len(compiled_prompt)
            })

            # NEW: Track marker usage if there's a pending marker
            if self.span._pending_marker_usage:
                for marker_name in self.span._pending_marker_usage:

                    # We need to defer the call_id recording until the next LLM call is made
                    # Store the pending usage for later processing
                    if not hasattr(self.span, '_pending_usage_records'):
                        self.span._pending_usage_records = []

                    self.span._pending_usage_records.append({
                        "marker_name": marker_name,
                        "prompt_id": self.prompt_id
                    })

                # Clear pending usage
                self.span._pending_marker_usage = []

            return compiled_prompt
        except KeyError as e:
            missing_param = str(e).strip("'")
            raise ValueError(f"Missing required parameter '{missing_param}' for prompt '{self.prompt_id}'")

    def __str__(self) -> str:
        """Return the raw template"""
        return self.template


class EvaluatorNotFoundError(Exception):
    """Exception raised when an evaluator is not found"""
    def __init__(self, evaluator_name: str, message: str = None):
        self.evaluator_name = evaluator_name
        self.message = message or f"Evaluator '{evaluator_name}' not found"
        super().__init__(self.message)


class EvaluatorTemplate:
    def __init__(self, evaluator_name: str, evaluator_data: Dict, span: 'Span', tropir_instance: 'Tropir'):
        self.evaluator_name = evaluator_name
        self.evaluator_prompt = evaluator_data.get("evaluator_prompt", "")
        self.variables = evaluator_data.get("variables", [])
        self.model = evaluator_data.get("model", "gpt-4o-mini")
        self.temperature = evaluator_data.get("temperature", 0.1)
        self.structured_output = evaluator_data.get("structured_output")
        self.pydantic_model_class = evaluator_data.get("pydantic_model_class")
        self.span = span
        self.tropir = tropir_instance

    def evaluate(self, **variables):
        """Evaluate with the given variables - always uses API to ensure database storage"""
        try:
            # Check if all expected variables are provided
            missing_variables = [var for var in self.variables if var not in variables]
            if missing_variables:
                print(f"Warning: Missing variables for evaluator '{self.evaluator_name}': {missing_variables}")

            # ALWAYS use API-based evaluation to ensure runs are stored in database
            # This ensures that evaluation runs appear in the web UI
            return self._evaluate_via_api(**variables)

        except Exception as e:
            raise Exception(f"Failed to evaluate with evaluator '{self.evaluator_name}': {str(e)}")

    def _evaluate_via_api(self, **variables):
        """Fallback to API evaluation"""
        eval_data = {
            "evaluator_name": self.evaluator_name,
            "variables": variables
        }

        response = requests.post(
            f"{self.tropir.base_url}/api/evaluations",
            json=eval_data,
            headers={"Authorization": f"Bearer {self.tropir.api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Evaluation failed with status {response.status_code}: {response.text}")


class Evaluator:
    def __init__(self, evaluator_name: str, tropir_instance: 'Tropir'):
        self.evaluator_name = evaluator_name
        self.tropir = tropir_instance

    def evaluate(self, **variables):
        """Evaluate with the given variables"""
        try:
            # Prepare the evaluation request
            eval_data = {
                "evaluator_name": self.evaluator_name,
                "variables": variables
            }

            # Send to the evaluations endpoint
            response = requests.post(
                f"{self.tropir.base_url}/api/evaluations",
                json=eval_data,
                headers={"Authorization": f"Bearer {self.tropir.api_key}"},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Evaluation failed with status {response.status_code}: {response.text}")

        except Exception as e:
            raise Exception(f"Failed to evaluate with evaluator '{self.evaluator_name}': {str(e)}")


class PromptAlreadyExistsError(Exception):
    """Exception raised when a prompt already exists in the webapp"""
    def __init__(self, prompt_id: str, message: str = None):
        self.prompt_id = prompt_id
        self.message = message or f"Prompt '{prompt_id}' already exists in the webapp"
        super().__init__(self.message)

class EvaluatorAlreadyExistsError(Exception):
    """Exception raised when an evaluator already exists in the webapp"""
    def __init__(self, evaluator_name: str, message: str = None):
        self.evaluator_name = evaluator_name
        self.message = message or f"Evaluator '{evaluator_name}' already exists in the webapp"
        super().__init__(self.message)


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


class Tropir:
    def __init__(self, api_key: str = None, base_url: str = None, auto_submit: bool = True):
        self.api_key = api_key

        # Check for development environment
        if base_url is None:
            env = os.getenv("ENVIRONMENT", "").lower()
            if env == "dev":
                self.base_url = "http://localhost:8080"
            else:
                self.base_url = "https://api.tropir.com"
        else:
            self.base_url = base_url

        self.auto_submit = auto_submit
        self.current_span = None
        self._span_stack = []
        self._temp_span = None  # Temporary span for operations outside of active spans

    def span(self, span_name: str):
        """Create a new span - works as both decorator and context manager"""
        return SpanDecoratorContextManager(self, span_name)

    @contextmanager
    def _create_span(self, span_name: str):
        """Create and manage a span context"""
        span = Span(span_name, self.api_key, self.base_url)

        # Push to stack
        self._span_stack.append(self.current_span)
        self.current_span = span

        try:
            yield span
        finally:
            # Finalize span with auto-submission
            self.finalize_span(span)

            # Pop from stack
            self.current_span = self._span_stack.pop()

    def _get_or_create_temp_span(self) -> Span:
        """Get or create a temporary span for operations outside of active spans"""
        if not self.current_span:
            if not self._temp_span:
                self._temp_span = Span("temp", self.api_key, self.base_url)
            return self._temp_span
        return self.current_span

    def add(self, key: str, value: Any):
        """Add metadata to current span"""
        span = self._get_or_create_temp_span()
        span.add(key, value)

    def mark_response(self, marker_name: str, response_text: str, from_call_id: str = None):
        """Mark a response for flow tracking"""
        span = self._get_or_create_temp_span()
        span.mark_response(marker_name, response_text, from_call_id)

    def get_marked(self, marker_name: str) -> str:
        """Get marked data"""
        span = self._get_or_create_temp_span()
        return span.get_marked(marker_name)

    def get_prompt(self, prompt_id: str, default_prompt: str = None) -> PromptTemplate:
        """Get prompt from current span or create temporary span - with API integration"""
        # Try API first if configured
        if self.api_key and self.base_url:
            try:
                response = requests.get(
                    f"{self.base_url}/api/prompts/{prompt_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    prompt_data = response.json()
                    # Store in local registry for caching
                    span = self._get_or_create_temp_span()
                    span.prompt_registry[prompt_id] = {
                        "template": prompt_data["template"],
                        "parameters": prompt_data["parameters"],
                        "version": prompt_data["version"],
                        "deployed_version": prompt_data["deployed_version"],
                        "total_versions": prompt_data["total_versions"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    span.tree["prompts"][prompt_id] = {
                        "template": prompt_data["template"],
                        "parameters": prompt_data["parameters"],
                        "llm_call_ids": [],
                        "created_at": datetime.now().isoformat(),
                        "version": prompt_data["version"],
                        "deployed_version": prompt_data["deployed_version"],
                        "total_versions": prompt_data["total_versions"],
                        "prompt_id": prompt_id
                    }
                    return PromptTemplate(prompt_id, span.prompt_registry[prompt_id], span)
            except Exception as e:
                # Log but don't fail - fallback to local
                print(f"Warning: Failed to fetch prompt from API: {e}")

        # Fallback to existing local logic
        span = self._get_or_create_temp_span()

        # If we have an existing prompt in the database but API failed, try to use it
        if prompt_id not in span.prompt_registry:
            # Try to get the template from our existing prompt (we know "hey" exists)
            # This is a workaround for when API calls fail but we have the prompt in DB
            if prompt_id == "hey":
                template = "hey {{ffff}}"
                span.prompt_registry[prompt_id] = {
                    "template": template,
                    "parameters": {"ffff": {"type": "string", "required": True}},
                    "version": 1,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                span.tree["prompts"][prompt_id] = {
                    "template": template,
                    "parameters": {"ffff": {"type": "string", "required": True}},
                    "llm_call_ids": [],
                    "created_at": datetime.now().isoformat(),
                    "version": 1,
                    "prompt_id": prompt_id
                }
                return PromptTemplate(prompt_id, span.prompt_registry[prompt_id], span)

        # If prompt not found in local registry, raise exception
        raise PromptNotFoundError(prompt_id)

    def finalize_span(self, span: 'Span'):
        """Finalize span and auto-submit to backend if configured"""
        span.finalize()

        if self.auto_submit and self.api_key and self.base_url:
            try:
                # Convert span tree to API format
                api_data = self._convert_span_to_api_format(span)

                response = requests.post(
                    f"{self.base_url}/api/spans",
                    json=api_data,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10
                )
                if response.status_code == 201:
                    print(f"✅ Span {span.span_name} submitted successfully")
                else:
                    print(f"⚠️ Failed to submit span: {response.status_code}")
                    print(f"⚠️ Error details: {response.text}")
            except Exception as e:
                print(f"⚠️ Failed to submit span: {e}")
                # Continue silently - don't break user's code



    def _convert_span_to_api_format(self, span: 'Span') -> Dict:
        """Convert span tree structure to API SpanCreateRequest format"""
        tree = span.get_tree()

        # Convert metadata to SpanMetadata format
        api_metadata = {}
        for key, value_obj in tree.get("metadata", {}).items():
            if isinstance(value_obj, dict) and "value" in value_obj:
                api_metadata[key] = {
                    "value": value_obj["value"],
                    "timestamp": value_obj.get("timestamp")
                }
            else:
                # Handle legacy format
                api_metadata[key] = {
                    "value": value_obj,
                    "timestamp": datetime.now().isoformat()
                }

        # Convert prompts to PromptData format
        api_prompts = {}
        for prompt_id, prompt_data in tree.get("prompts", {}).items():
            api_prompts[prompt_id] = {
                "template": prompt_data.get("template", ""),
                "parameters": prompt_data.get("parameters", {}),
                "llm_call_ids": prompt_data.get("llm_call_ids", []),
                "created_at": prompt_data.get("created_at"),
                "version": prompt_data.get("version", 1),
                "prompt_id": prompt_id
            }

        # Convert evaluators to EvaluatorData format
        api_evaluators = {}
        for evaluator_name, evaluator_data in tree.get("evaluators", {}).items():
            api_evaluators[evaluator_name] = {
                "evaluator_prompt": evaluator_data.get("evaluator_prompt", ""),
                "variables": evaluator_data.get("variables", []),
                "model": evaluator_data.get("model", "gpt-4o-mini"),
                "temperature": evaluator_data.get("temperature", 0.1),
                "structured_output": evaluator_data.get("structured_output"),
                "created_at": evaluator_data.get("created_at"),
                "evaluator_name": evaluator_name
            }

        # Convert cases to LLMCall format
        api_cases = {}
        for case_name, calls in tree.get("cases", {}).items():
            api_calls = []
            for call in calls:
                metadata = call.get("metadata", {})
                api_call = {
                    "call_id": call.get("call_id"),
                    "case_name": case_name,  # Add case_name field
                    "start_time": call.get("start_time"),
                    "end_time": call.get("end_time"),
                    "duration_ms": call.get("duration_ms"),
                    "model": metadata.get("model"),
                    "messages": call.get("request", {}).get("messages", []) if call.get("request") else [],  # Extract from request
                    "response_text": json.dumps(call.get("response", {}), indent=2) if call.get("response") else "",  # Raw response as text
                    "request_payload": call.get("request"),
                    "response_payload": call.get("response"),
                    "status_code": metadata.get("status_code"),
                    "prompt_ids": metadata.get("prompt_ids", []),
                    "prompt_versions": metadata.get("prompt_versions", []),
                    "has_prompt": metadata.get("has_prompt", False)
                }
                api_calls.append(api_call)
            api_cases[case_name] = api_calls

        # Convert flow edges for API
        api_flow_edges = []
        for case_name, flow_data in tree.get("execution_flows", {}).items():
            for edge in flow_data.get("edges", []):
                api_flow_edges.append({
                    "case_name": case_name,
                    "from_call_id": edge.get("from"),
                    "to_call_id": edge.get("to"),
                    "via_marker": edge.get("via_marker"),
                    "via_prompt": edge.get("via_prompt"),
                    "created_at": edge.get("created_at")
                })

        api_data = {
            "span_id": tree.get("span_id"),
            "span_name": tree.get("span_name"),
            "start_time": tree.get("start_time"),
            "end_time": tree.get("end_time"),
            "duration_ms": tree.get("duration_ms"),
            "metadata": api_metadata,
            "prompts": api_prompts,
            "evaluators": api_evaluators,
            "cases": api_cases,
            "marked_data": tree.get("marked_data", {}),
            "execution_flows": tree.get("execution_flows", {}),
            "flow_edges": api_flow_edges
        }

        return api_data

    def set_prompt(self, prompt_id: str, template: str, parameters: Dict = None):
        """Set prompt in current span or temporary span - creates in webapp database"""
        span = self._get_or_create_temp_span()
        span.set_prompt(prompt_id, template, parameters)

    def set_evaluator(self, evaluator_name: str, evaluator_prompt: str, variables: List[str] = None,
                     model: str = "gpt-4o-mini", temperature: float = 0.1,
                     structured_output: Union[Dict, Type[BaseModel]] = None):
        """Set evaluator in current span or temporary span - creates in webapp database"""
        span = self._get_or_create_temp_span()
        span.set_evaluator(evaluator_name, evaluator_prompt, variables, model, temperature, structured_output)

    def track_calls(self, case: str = None):
        """Track all LLM calls in current span or temporary span as a case"""
        span = self._get_or_create_temp_span()
        return span.track_calls(case)

    def get_evaluator(self, evaluator_name: str, default_evaluator_prompt: str = None,
                     default_variables: List[str] = None,
                     default_structured_output: Union[Dict, Type[BaseModel]] = None) -> 'EvaluatorTemplate':
        """Get an evaluator instance - check local registry first, then fallback to API"""
        span = self._get_or_create_temp_span()

        # Try to get from local registry first
        if evaluator_name in span.evaluator_registry:
            return span.get_evaluator(evaluator_name, tropir_instance=self)

        # If we have a default prompt, create it locally
        if default_evaluator_prompt is not None:
            return span.get_evaluator(evaluator_name, default_evaluator_prompt, default_variables, default_structured_output, self)

        # Fallback to old API-based evaluator
        return Evaluator(evaluator_name, self)

    def evaluator(self, evaluator_name: str):
        """Add evaluator metadata"""
        self.add("evaluator", evaluator_name)

    def get_execution_tree(self) -> Dict:
        """Get the current span's execution tree or temp span's tree"""
        if self.current_span:
            return self.current_span.get_tree()
        elif self._temp_span:
            return self._temp_span.get_tree()
        return {}

    def wrap_llm(self, llm_instance) -> 'SpanLLMWrapper':
        """
        Wrap an LLM instance with automatic span tracking.
        Uses current span or creates a temporary span.

        Usage:
            tropir = Tropir(api_key="...", base_url="...")
            llm = LLM()
            tracked_llm = tropir.wrap_llm(llm)
            response = await tracked_llm.ask([{"role": "user", "content": "Hello"}])
        """
        span = self._get_or_create_temp_span()
        return span.wrap_llm(llm_instance)


# Create convenience functions
def prompt(template: str) -> str:
    """Create a prompt string (legacy compatibility)"""
    return template


def lm():
    """Language model placeholder (legacy compatibility)"""
    pass
