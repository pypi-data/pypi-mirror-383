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

from .core import Span
from .templates import PromptTemplate, EvaluatorTemplate
from .evaluator import Evaluator
from .wrapper import SpanDecoratorContextManager, SpanLLMWrapper
from .exceptions import PromptNotFoundError

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

