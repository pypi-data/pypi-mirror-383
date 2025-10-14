"""
Base client with common functionality
"""

import os
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

from ..models.api_types import (
    MultiAgentTrace,
    TraceRewardRequest,
    MultiAgentTraceResponse,
)
from ..models.common_types import ModelCore
from ..models import EvaluationRequest, EvaluationResponse, BinaryEvaluationResponse
from ..adapters import AdapterFactory
from ..utils import validate_api_key
from ..exceptions import MalformedError, get_exception_for_status_code
from .types import MessagesType, ToolsType, ResultType

# API endpoint constants
REWARD_ENDPOINT = "/api/v1/evals/reward"
BINARY_ENDPOINT = "/api/v1/evals/binary"
TRACE_ENDPOINT = "/api/v1/evals/trace"


class BaseClient(ABC):
    """Abstract base client with template method pattern"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://platform.composo.ai",
        num_retries: int = 1,
        model_core: Optional[str] = None,
        timeout: float = 60.0,
    ):
        # Auto-load API key from environment variable if not provided
        if api_key is None:
            api_key = os.getenv("COMPOSO_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key is required. Either pass it as a parameter or set the "
                    "COMPOSO_API_KEY environment variable."
                )

        validate_api_key(api_key)

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.num_retries = max(1, num_retries)
        self.model_core = model_core
        self.timeout = timeout
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        self._closed = False

    def _get_sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client with connection pooling"""
        if self._closed:
            raise RuntimeError("Client has been closed")
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            )
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client with connection pooling"""
        if self._closed:
            raise RuntimeError("Client has been closed")
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            )
        return self._async_client

    def close(self):
        """Close sync HTTP client"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        self._closed = True

    async def aclose(self):
        """Close async HTTP client"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
        self._closed = True

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and convert errors to exceptions"""
        if 200 <= response.status_code < 300:
            return response.json()
        # Pass the response body to the exception
        try:
            response_body = response.text
        except Exception:
            response_body = None

        # Use response body as the main message if available, otherwise use status code
        if response_body:
            error_message = response_body
        else:
            error_message = f"HTTP {response.status_code}"

        raise get_exception_for_status_code(
            response.status_code, error_message, response_body
        )

    def _post(
        self, endpoint: str, data: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Synchronous POST request with connection reuse"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        client = self._get_sync_client()
        response = client.post(url, json=data, headers=headers)
        return self._handle_response(response)

    async def _apost(
        self, endpoint: str, data: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Asynchronous POST request with connection reuse"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        client = self._get_async_client()
        response = await client.post(url, json=data, headers=headers)
        return self._handle_response(response)

    def _is_binary_criteria(self, criteria: str) -> bool:
        """Check if criteria is for binary evaluation"""
        if not criteria:
            return False
        criteria_lower = criteria.lower().strip()
        return (
            criteria_lower.startswith("response passes")
            or criteria_lower.startswith("response fails")
            or criteria_lower.startswith("tool call passes if")
            or criteria_lower.startswith("tool call fails if")
        )

    def _prepare_evaluation_request(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        criteria: Union[str, List[str]],
    ) -> EvaluationRequest:
        """Prepare evaluation request with common validation and processing"""

        # Process result if provided first to get the appropriate adapter
        final_messages = messages.copy()
        final_system = system
        final_tools = tools

        if result is not None:
            adapter = AdapterFactory.get_adapter(result)
            if adapter:
                # Process result using the adapter
                final_messages, final_system, final_tools = adapter.process_result(
                    messages, result, system, tools
                )
            else:
                raise MalformedError("Unsupported result format")

        # Use criteria as-is (no validation)
        normalized_criteria = criteria

        return EvaluationRequest(
            messages=final_messages,
            system_message=final_system,  # Pass system message as-is
            tools=final_tools,
            evaluation_criteria=normalized_criteria,
            model_core=self.model_core,
        )

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for API requests"""
        return {
            "API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "composo-python-sdk/0.1.0",
        }

    def _get_endpoint(
        self, evaluation_request: EvaluationRequest, single_criterion: str
    ) -> str:
        """Determine the appropriate endpoint based on request type and criteria"""
        if evaluation_request.trace is not None:
            return TRACE_ENDPOINT
        return (
            BINARY_ENDPOINT
            if self._is_binary_criteria(single_criterion)
            else REWARD_ENDPOINT
        )

    def _process_evaluation_response(
        self, response_data: Dict[str, Any], single_criterion: str
    ) -> EvaluationResponse:
        """Process evaluation response for both binary and reward criteria"""
        if self._is_binary_criteria(single_criterion):
            # Convert binary response to score format
            binary_response = BinaryEvaluationResponse(**response_data)
            score = 1.0 if binary_response.passed else 0.0
            return EvaluationResponse(
                score=score, explanation=binary_response.explanation
            )
        else:
            return EvaluationResponse.from_dict(response_data)

    @abstractmethod
    def _make_request(
        self, request_data: Dict[str, Any], endpoint: str
    ) -> Dict[str, Any]:
        """Make HTTP request - implemented by concrete clients"""
        pass

    @abstractmethod
    def _evaluate_multiple_criteria(
        self,
        messages: MessagesType,
        system: Optional[str],
        tools: ToolsType,
        result: ResultType,
        criteria: List[str],
    ) -> List[EvaluationResponse]:
        """Evaluate multiple criteria - implemented by concrete clients"""
        pass

    def _prepare_trace_request(
        self,
        trace: MultiAgentTrace,
        criterion: str,
        model_core: Optional[ModelCore],
    ) -> Dict[str, Any]:
        """Prepare trace evaluation request"""
        # Only include model_core in kwargs if it's not None
        kwargs = {
            "trace": trace,
            "evaluation_criteria": criterion,
        }
        if model_core is not None:
            kwargs["model_core"] = model_core

        trace_reward_request = TraceRewardRequest(**kwargs)
        endpoint = self._get_endpoint(trace_reward_request, criterion)
        request_data = trace_reward_request.model_dump(exclude_none=True)
        return {"endpoint": endpoint, "request_data": request_data}

    def _process_trace_response(
        self, response_data: Dict[str, Any]
    ) -> MultiAgentTraceResponse:
        """Process trace evaluation response"""
        return MultiAgentTraceResponse(**response_data)
