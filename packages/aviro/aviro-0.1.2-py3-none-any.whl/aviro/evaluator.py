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
    from .tropir import Tropir

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

