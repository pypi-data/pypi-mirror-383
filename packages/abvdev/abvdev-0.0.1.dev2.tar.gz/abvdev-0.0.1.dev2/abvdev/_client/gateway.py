"""ABV Gateway client for AI inference with automatic tracing.

This module provides an OpenAI-compatible interface to the ABV AI Gateway
with automatic tracing integration. All gateway calls are automatically
traced as generation observations in ABV.
"""

import json
import logging
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
)

import httpx
from opentelemetry import trace as otel_trace_api

from abvdev._client.attributes import ABVOtelSpanAttributes
from abvdev.logger import abv_logger
from abvdev.types import MapValue, SpanLevel

if TYPE_CHECKING:
    from abvdev._client.client import ABV
    from abvdev._client.span import ABVGeneration


# Type definitions
class ChatMessage(TypedDict, total=False):
    """Message in a chat conversation."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_call_id: Optional[str]


class ChatCompletionTool(TypedDict, total=False):
    """Tool definition for chat completions."""
    type: Literal["function"]
    function: Dict[str, Any]


class ChatCompletionParams(TypedDict, total=False):
    """Parameters for chat completion requests."""
    provider: Literal["openai", "anthropic", "gemini"]
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float]
    max_tokens: Optional[int]
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    stream: Optional[bool]
    tools: Optional[List[ChatCompletionTool]]
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    response_format: Optional[Dict[str, str]]
    stop: Optional[Union[str, List[str]]]
    user: Optional[str]
    top_k: Optional[float]


class ChatCompletionResponse(TypedDict):
    """Response from chat completion endpoint."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]]
    system_fingerprint: Optional[str]


class GatewayClient:
    """Client for ABV AI Gateway with automatic tracing.

    This client provides an OpenAI-compatible interface to the ABV AI Gateway.
    All requests are automatically traced as generation observations in ABV.

    Example:
        ```python
        from abvdev import ABV

        abv = ABV(
            api_key="sk-abv-...",
            gateway={"region": "us"}
        )

        # Synchronous usage
        response = abv.gateway.chat.completions.create(
            provider="openai",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}]
        )

        # Async usage
        response = await abv.gateway.chat.completions.create_async(
            provider="openai",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}],
            stream=True
        )
        ```
    """

    def __init__(self, api_key: str, region: str = "us", abv_client: Optional["ABV"] = None):
        """Initialize the gateway client.

        Args:
            api_key: ABV API key for authentication
            region: Gateway region ("us" or "eu")
            abv_client: Reference to parent ABV client for tracing
        """
        self.base_url = (
            "https://eu.gateway.abv.dev"
            if region == "eu"
            else "https://gateway.abv.dev"
        )
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "abv-python-sdk",
        }
        self._abv_client = abv_client
        self.chat = ChatCompletions(self)

        abv_logger.debug(f"Initialized GatewayClient with region={region}, base_url={self.base_url}")


class ChatCompletions:
    """Chat completions interface for the gateway."""

    def __init__(self, gateway_client: GatewayClient):
        """Initialize chat completions interface.

        Args:
            gateway_client: Parent gateway client
        """
        self.gateway = gateway_client
        self.completions = self  # For OpenAI compatibility

    def create(
        self,
        provider: Literal["openai", "anthropic", "gemini"],
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        tools: Optional[List[ChatCompletionTool]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, str]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        user: Optional[str] = None,
        top_k: Optional[float] = None,
    ) -> Union[ChatCompletionResponse, AsyncIterator[Dict[str, Any]]]:
        """Create a chat completion (synchronous).

        Args:
            provider: AI provider to use
            model: Model identifier (without provider prefix)
            messages: List of messages in the conversation
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stream: Whether to stream the response
            tools: List of available tools
            tool_choice: How to choose tools
            response_format: Output format constraints
            stop: Stop sequences
            user: User identifier
            top_k: Top-k sampling parameter

        Returns:
            ChatCompletionResponse for non-streaming, iterator for streaming
        """
        # Get active span for context propagation
        active_span = otel_trace_api.get_current_span()

        # Build model parameters
        model_parameters = {}
        if temperature is not None:
            model_parameters["temperature"] = temperature
        if max_tokens is not None:
            model_parameters["max_tokens"] = max_tokens
        if top_p is not None:
            model_parameters["top_p"] = top_p
        if frequency_penalty is not None:
            model_parameters["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            model_parameters["presence_penalty"] = presence_penalty
        if top_k is not None:
            model_parameters["top_k"] = top_k

        # Format model with provider prefix
        full_model_name = f"{provider}/{model}"

        # Create generation observation
        generation = None
        if self.gateway._abv_client:
            generation = self.gateway._abv_client.start_observation(
                name="gateway-chat-completion",
                as_type="generation",
                input=messages,
                model=full_model_name,
                model_parameters=model_parameters if model_parameters else None,
                metadata={
                    "stream": stream,
                    "provider": provider,
                    "tools": [t["function"]["name"] for t in tools] if tools else None,
                    "tool_choice": tool_choice,
                    "response_format": response_format,
                    "stop": stop,
                    "user": user,
                },
            )

        try:
            # Build request headers
            headers = dict(self.gateway.headers)
            if generation:
                headers["X-ABV-Trace-Id"] = generation.trace_id
                headers["X-ABV-Span-Id"] = generation.id

            # Build request body
            request_body = {
                "model": full_model_name,
                "messages": messages,
                "stream": stream,
            }

            # Add optional parameters
            if temperature is not None:
                request_body["temperature"] = temperature
            if max_tokens is not None:
                request_body["max_tokens"] = max_tokens
            if top_p is not None:
                request_body["top_p"] = top_p
            if frequency_penalty is not None:
                request_body["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                request_body["presence_penalty"] = presence_penalty
            if tools:
                request_body["tools"] = tools
            if tool_choice:
                request_body["tool_choice"] = tool_choice
            if response_format:
                request_body["response_format"] = response_format
            if stop:
                request_body["stop"] = stop
            if user:
                request_body["user"] = user
            if top_k is not None:
                request_body["top_k"] = top_k

            # Make synchronous request
            with httpx.Client() as client:
                response = client.post(
                    f"{self.gateway.base_url}/ai/chat/completions",
                    headers=headers,
                    json=request_body,
                    timeout=120.0,
                )

                if not response.is_success:
                    error_msg = f"Gateway error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except:
                        pass
                    raise Exception(error_msg)

                # Handle streaming response
                if stream:
                    return self._handle_stream_sync(response, generation)

                # Handle non-streaming response
                data = response.json()

                # Update observation with response data
                if generation:
                    generation.update(
                        output=data.get("choices", [{}])[0].get("message"),
                        model=data.get("model"),
                        usage_details={
                            "prompt_tokens": data.get("usage", {}).get("prompt_tokens"),
                            "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                            "total_tokens": data.get("usage", {}).get("total_tokens"),
                        } if data.get("usage") else None,
                        metadata={
                            "finish_reason": data.get("choices", [{}])[0].get("finish_reason"),
                            "system_fingerprint": data.get("system_fingerprint"),
                        },
                    )

                abv_logger.debug(f"Completed chat completion: model={data.get('model')}, usage={data.get('usage')}")

                return cast(ChatCompletionResponse, data)

        except Exception as e:
            # Update observation with error
            if generation:
                generation.update(
                    level="ERROR",
                    status_message=str(e),
                )

            abv_logger.error(f"Chat completion failed: {e}")
            raise

        finally:
            # End observation for non-streaming requests
            if generation and not stream:
                generation.end()

    async def create_async(
        self,
        provider: Literal["openai", "anthropic", "gemini"],
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stream: bool = False,
        tools: Optional[List[ChatCompletionTool]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, str]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        user: Optional[str] = None,
        top_k: Optional[float] = None,
    ) -> Union[ChatCompletionResponse, AsyncIterator[Dict[str, Any]]]:
        """Create a chat completion (asynchronous).

        Same parameters and behavior as create(), but async.

        Example:
            ```python
            response = await abv.gateway.chat.completions.create_async(
                provider="openai",
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello!"}],
                stream=True
            )

            # Handle streaming response
            async for chunk in response:
                print(chunk["choices"][0]["delta"].get("content", ""), end="")
            ```
        """
        # Get active span for context propagation
        active_span = otel_trace_api.get_current_span()

        # Build model parameters
        model_parameters = {}
        if temperature is not None:
            model_parameters["temperature"] = temperature
        if max_tokens is not None:
            model_parameters["max_tokens"] = max_tokens
        if top_p is not None:
            model_parameters["top_p"] = top_p
        if frequency_penalty is not None:
            model_parameters["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            model_parameters["presence_penalty"] = presence_penalty
        if top_k is not None:
            model_parameters["top_k"] = top_k

        # Format model with provider prefix
        full_model_name = f"{provider}/{model}"

        # Create generation observation
        generation = None
        if self.gateway._abv_client:
            generation = self.gateway._abv_client.start_observation(
                name="gateway-chat-completion",
                as_type="generation",
                input=messages,
                model=full_model_name,
                model_parameters=model_parameters if model_parameters else None,
                metadata={
                    "stream": stream,
                    "provider": provider,
                    "tools": [t["function"]["name"] for t in tools] if tools else None,
                    "tool_choice": tool_choice,
                    "response_format": response_format,
                    "stop": stop,
                    "user": user,
                },
            )

        try:
            # Build request headers
            headers = dict(self.gateway.headers)
            if generation:
                headers["X-ABV-Trace-Id"] = generation.trace_id
                headers["X-ABV-Span-Id"] = generation.id

            # Build request body (same as sync version)
            request_body = {
                "model": full_model_name,
                "messages": messages,
                "stream": stream,
            }

            # Add optional parameters
            if temperature is not None:
                request_body["temperature"] = temperature
            if max_tokens is not None:
                request_body["max_tokens"] = max_tokens
            if top_p is not None:
                request_body["top_p"] = top_p
            if frequency_penalty is not None:
                request_body["frequency_penalty"] = frequency_penalty
            if presence_penalty is not None:
                request_body["presence_penalty"] = presence_penalty
            if tools:
                request_body["tools"] = tools
            if tool_choice:
                request_body["tool_choice"] = tool_choice
            if response_format:
                request_body["response_format"] = response_format
            if stop:
                request_body["stop"] = stop
            if user:
                request_body["user"] = user
            if top_k is not None:
                request_body["top_k"] = top_k

            # Make async request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gateway.base_url}/ai/chat/completions",
                    headers=headers,
                    json=request_body,
                    timeout=120.0,
                )

                if not response.is_success:
                    error_msg = f"Gateway error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except:
                        pass
                    raise Exception(error_msg)

                # Handle streaming response
                if stream:
                    return self._handle_stream_async(response, generation)

                # Handle non-streaming response
                data = response.json()

                # Update observation with response data
                if generation:
                    generation.update(
                        output=data.get("choices", [{}])[0].get("message"),
                        model=data.get("model"),
                        usage_details={
                            "prompt_tokens": data.get("usage", {}).get("prompt_tokens"),
                            "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                            "total_tokens": data.get("usage", {}).get("total_tokens"),
                        } if data.get("usage") else None,
                        metadata={
                            "finish_reason": data.get("choices", [{}])[0].get("finish_reason"),
                            "system_fingerprint": data.get("system_fingerprint"),
                        },
                    )

                abv_logger.debug(f"Completed async chat completion: model={data.get('model')}, usage={data.get('usage')}")

                return cast(ChatCompletionResponse, data)

        except Exception as e:
            # Update observation with error
            if generation:
                generation.update(
                    level="ERROR",
                    status_message=str(e),
                )

            abv_logger.error(f"Async chat completion failed: {e}")
            raise

        finally:
            # End observation for non-streaming requests
            if generation and not stream:
                generation.end()

    def _handle_stream_sync(self, response: httpx.Response, generation: Optional["ABVGeneration"]):
        """Handle synchronous streaming response.

        Args:
            response: HTTP response with SSE stream
            generation: ABV generation observation to update

        Yields:
            Chat completion chunks
        """
        # This would need to be implemented with proper SSE parsing
        # For now, returning a simple iterator
        def stream_generator():
            accumulated = {
                "content": "",
                "tool_calls": [],
                "usage": None,
                "model": None,
                "finish_reason": None,
            }

            try:
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)

                            # Accumulate content
                            if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                                accumulated["content"] += chunk["choices"][0]["delta"]["content"]

                            # Track model name
                            if chunk.get("model"):
                                accumulated["model"] = chunk["model"]

                            # Track finish reason
                            if chunk.get("choices", [{}])[0].get("finish_reason"):
                                accumulated["finish_reason"] = chunk["choices"][0]["finish_reason"]

                            # Track usage (usually in final chunk)
                            if chunk.get("usage"):
                                accumulated["usage"] = chunk["usage"]

                            yield chunk

                        except json.JSONDecodeError:
                            continue

                # Update observation with accumulated data
                if generation:
                    generation.update(
                        output={"role": "assistant", "content": accumulated["content"]},
                        model=accumulated["model"],
                        usage_details={
                            "prompt_tokens": accumulated["usage"].get("prompt_tokens"),
                            "completion_tokens": accumulated["usage"].get("completion_tokens"),
                            "total_tokens": accumulated["usage"].get("total_tokens"),
                        } if accumulated["usage"] else None,
                        metadata={"finish_reason": accumulated["finish_reason"]},
                    )
                    generation.end()

            except Exception as e:
                if generation:
                    generation.update(level="ERROR", status_message=str(e))
                    generation.end()
                raise

        return stream_generator()

    async def _handle_stream_async(self, response: httpx.Response, generation: Optional["ABVGeneration"]):
        """Handle asynchronous streaming response.

        Args:
            response: HTTP response with SSE stream
            generation: ABV generation observation to update

        Yields:
            Chat completion chunks
        """
        accumulated = {
            "content": "",
            "tool_calls": [],
            "usage": None,
            "model": None,
            "finish_reason": None,
        }

        try:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)

                        # Accumulate content
                        if chunk.get("choices", [{}])[0].get("delta", {}).get("content"):
                            accumulated["content"] += chunk["choices"][0]["delta"]["content"]

                        # Track model name
                        if chunk.get("model"):
                            accumulated["model"] = chunk["model"]

                        # Track finish reason
                        if chunk.get("choices", [{}])[0].get("finish_reason"):
                            accumulated["finish_reason"] = chunk["choices"][0]["finish_reason"]

                        # Track usage (usually in final chunk)
                        if chunk.get("usage"):
                            accumulated["usage"] = chunk["usage"]

                        yield chunk

                    except json.JSONDecodeError:
                        continue

            # Update observation with accumulated data
            if generation:
                generation.update(
                    output={"role": "assistant", "content": accumulated["content"]},
                    model=accumulated["model"],
                    usage_details={
                        "prompt_tokens": accumulated["usage"].get("prompt_tokens"),
                        "completion_tokens": accumulated["usage"].get("completion_tokens"),
                        "total_tokens": accumulated["usage"].get("total_tokens"),
                    } if accumulated["usage"] else None,
                    metadata={"finish_reason": accumulated["finish_reason"]},
                )
                generation.end()

        except Exception as e:
            if generation:
                generation.update(level="ERROR", status_message=str(e))
                generation.end()
            raise


def parse_sse_chunk(text: str) -> List[Dict[str, Any]]:
    """Parse Server-Sent Events from a text buffer.

    Args:
        text: Raw SSE text to parse

    Returns:
        List of parsed event objects
    """
    events = []
    lines = text.split("\n")

    for line in lines:
        trimmed_line = line.strip()

        if trimmed_line.startswith("data: "):
            data = trimmed_line[6:]

            # Skip the [DONE] marker
            if data == "[DONE]":
                continue

            try:
                parsed = json.loads(data)
                events.append(parsed)
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                abv_logger.debug(f"Failed to parse SSE chunk: {data}")

    return events