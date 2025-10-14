#!/usr/bin/env python3
#
# Unified interface for LLM providers using OpenAI format
# https://github.com/muxi-ai/onellm
#
# Copyright (C) 2025 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Chat completion functionality for OneLLM.

This module provides a ChatCompletion class that can be used to create chat
completions from various providers in a manner compatible with OpenAI's API.
"""

import logging
import warnings
from collections.abc import AsyncGenerator
from typing import Any

from .models import ChatCompletionChunk, ChatCompletionResponse
from .providers.base import get_provider_with_fallbacks
from .utils.async_helpers import run_async
from .utils.fallback import FallbackConfig
from .validators import validate_messages, validate_model_name, validate_stream


class ChatCompletion:
    """Class for creating chat completions with various providers."""

    logger = logging.getLogger("onellm.chat_completion")

    @classmethod
    def _process_capabilities(
        cls,
        provider: Any,
        messages: list[dict[str, Any]],
        stream: bool,
        kwargs: dict[str, Any]
    ) -> tuple:
        """
        Process messages and kwargs based on provider capabilities.

        This method checks if the provider supports requested features like JSON mode,
        streaming, vision (image content), and audio input. It modifies the messages
        and parameters accordingly to ensure compatibility with the provider's capabilities.

        Args:
            provider: The provider instance
            messages: The messages to process
            stream: Whether streaming was requested
            kwargs: Additional kwargs to process

        Returns:
            Tuple of (processed_messages, stream_flag, processed_kwargs)
        """
        processed_kwargs = dict(kwargs)

        # Handle JSON mode (response_format parameter)
        if "response_format" in kwargs:
            response_format = kwargs["response_format"]

            # Check if this is a JSON mode request
            is_json_mode = (
                isinstance(response_format, dict) and
                response_format.get("type") == "json_object"
            )

            if is_json_mode and not provider.json_mode_support:
                # Provider doesn't support JSON mode, remove parameter and warn
                processed_kwargs.pop("response_format", None)
                warnings.warn(
                    "The selected provider does not support JSON mode. "
                    "The 'response_format' parameter will be ignored.",
                    UserWarning,
                    stacklevel=2
                )

                # Add a system message to request JSON format if not already present
                has_system_message = False
                for msg in messages:
                    if msg.get("role") == "system":
                        has_system_message = True
                        if "json" not in msg.get("content", "").lower():
                            # Append JSON instruction to existing system message
                            msg["content"] += " Please provide your response in valid JSON format."
                        break

                if not has_system_message:
                    # Add a new system message requesting JSON
                    messages_copy = list(messages)  # Create a copy to avoid modifying the original
                    messages_copy.insert(0, {
                        "role": "system",
                        "content": "Please provide your response in valid JSON format."
                    })
                    messages = messages_copy

        # Check if streaming is requested but not supported
        if stream and not provider.streaming_support:
            stream = False
            warnings.warn(
                "The selected provider does not support streaming. "
                "The request will be processed in non-streaming mode.",
                UserWarning,
                stacklevel=2
            )

        # Check for vision (image) content when provider doesn't support it
        if not provider.vision_support:
            has_image_content = False
            # Scan all messages to check if any contain image content
            for message in messages:
                content = message.get("content", "")
                # Check for image content in list format
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "image_url" or item.get("type") == "image":
                            has_image_content = True
                            break
                    if has_image_content:
                        break

            if has_image_content:
                warnings.warn(
                    "The selected provider does not support vision/image inputs. "
                    "Image content will be removed from the messages.",
                    UserWarning,
                    stacklevel=2
                )

                # Remove image content from messages
                processed_messages = []
                for message in messages:
                    content = message.get("content", "")
                    if isinstance(content, list):
                        # Filter out image content
                        text_content = ""
                        for item in content:
                            if item.get("type") == "text":
                                text_content += item.get("text", "") + "\n"

                        if text_content:
                            processed_message = dict(message)
                            processed_message["content"] = text_content.strip()
                            processed_messages.append(processed_message)
                    else:
                        # Keep non-list content unchanged
                        processed_messages.append(message)

                messages = processed_messages

        # Check for audio content when provider doesn't support it
        if not provider.audio_input_support:
            has_audio_content = False
            # Scan all messages to check if any contain audio content
            for message in messages:
                content = message.get("content", "")
                # Check for audio content in list format
                if isinstance(content, list):
                    for item in content:
                        if item.get("type") == "audio_url" or item.get("type") == "audio":
                            has_audio_content = True
                            break
                    if has_audio_content:
                        break

            if has_audio_content:
                warnings.warn(
                    "The selected provider does not support audio inputs. "
                    "Audio content will be removed from the messages.",
                    UserWarning,
                    stacklevel=2
                )

                # Remove audio content from messages
                processed_messages = []
                for message in messages:
                    content = message.get("content", "")
                    if isinstance(content, list):
                        # Filter out audio content
                        filtered_content = []
                        for item in content:
                            if item.get("type") not in ["audio_url", "audio"]:
                                filtered_content.append(item)

                        if filtered_content:
                            processed_message = dict(message)
                            processed_message["content"] = filtered_content
                            processed_messages.append(processed_message)
                        elif any(item.get("type") == "text" for item in content):
                            # If only text remains, convert to simple format
                            text_content = ""
                            for item in content:
                                if item.get("type") == "text":
                                    text_content += item.get("text", "") + "\n"

                            if text_content:
                                processed_message = dict(message)
                                processed_message["content"] = text_content.strip()
                                processed_messages.append(processed_message)
                    else:
                        # Keep non-list content unchanged
                        processed_messages.append(message)

                messages = processed_messages

        return messages, stream, processed_kwargs

    @classmethod
    def _accumulate_and_cache_stream(cls, stream_generator, cache, model, messages, **kwargs):
        """
        Wrap a streaming response to accumulate chunks and cache the complete response.

        This generator yields chunks as they arrive while building the complete response
        in the background. Once streaming completes, it caches the full response.

        Args:
            stream_generator: Generator yielding ChatCompletionChunk objects
            cache: Cache instance to store the complete response
            model: Model identifier
            messages: Original messages
            **kwargs: Additional parameters

        Yields:
            ChatCompletionChunk objects from the original stream
        """
        accumulated_content = ""
        last_chunk = None

        # Iterate through the stream, yielding each chunk
        for chunk in stream_generator:
            last_chunk = chunk

            # Extract content from delta
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    accumulated_content += content

            yield chunk

        # After streaming completes, cache the complete response
        if last_chunk and accumulated_content:
            # Create a complete ChatCompletionResponse from accumulated content
            complete_response = ChatCompletionResponse(
                id=last_chunk.id if hasattr(last_chunk, 'id') else "cached",
                object="chat.completion",
                model=last_chunk.model if hasattr(last_chunk, 'model') else model,
                created=last_chunk.created if hasattr(last_chunk, 'created') else 0,
                choices=[
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": accumulated_content},
                        "finish_reason": "stop",
                    }
                ],
            )
            cache.set(model, messages, complete_response, **kwargs)

    @classmethod
    async def _aaccumulate_and_cache_stream(cls, stream_generator, cache, model, messages, **kwargs):
        """
        Async version of _accumulate_and_cache_stream.

        Wrap an async streaming response to accumulate chunks and cache the complete response.

        Args:
            stream_generator: Async generator yielding ChatCompletionChunk objects
            cache: Cache instance to store the complete response
            model: Model identifier
            messages: Original messages
            **kwargs: Additional parameters

        Yields:
            ChatCompletionChunk objects from the original stream
        """
        accumulated_content = ""
        last_chunk = None

        # Iterate through the async stream, yielding each chunk
        async for chunk in stream_generator:
            last_chunk = chunk

            # Extract content from delta
            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                delta = chunk.choices[0].get('delta', {})
                content = delta.get('content', '')
                if content:
                    accumulated_content += content

            yield chunk

        # After streaming completes, cache the complete response
        if last_chunk and accumulated_content:
            # Create a complete ChatCompletionResponse from accumulated content
            complete_response = ChatCompletionResponse(
                id=last_chunk.id if hasattr(last_chunk, 'id') else "cached",
                object="chat.completion",
                model=last_chunk.model if hasattr(last_chunk, 'model') else model,
                created=last_chunk.created if hasattr(last_chunk, 'created') else 0,
                choices=[
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": accumulated_content},
                        "finish_reason": "stop",
                    }
                ],
            )
            cache.set(model, messages, complete_response, **kwargs)

    @classmethod
    def create(
        cls,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        fallback_models: list[str] | None = None,
        fallback_config: dict[str, Any] | None = None,
        retries: int = 0,
        **kwargs
    ) -> ChatCompletionResponse | AsyncGenerator[ChatCompletionChunk, None]:
        """
        Create a chat completion.

        This synchronous method creates a chat completion using the specified model.
        It supports fallback models if the primary model fails, and can retry the
        primary model before falling back. It handles both streaming and non-streaming
        responses.

        Args:
            model: Model name with provider prefix (e.g., 'openai/gpt-4')
            messages: List of messages in the conversation
            stream: Whether to stream the response
            fallback_models: Optional list of models to try if the primary model fails
            fallback_config: Optional configuration for fallback behavior
            retries: Number of times to retry the primary model before falling back (default: 0)
            **kwargs: Additional model parameters

        Returns:
            ChatCompletionResponse or a generator yielding ChatCompletionChunk objects

        Example:
            >>> response = ChatCompletion.create(
            ...     model="openai/gpt-4",
            ...     messages=[
            ...         {"role": "system", "content": "You are a helpful assistant."},
            ...         {"role": "user", "content": "Hello, how are you?"}
            ...     ],
            ...     fallback_models=["anthropic/claude-3-haiku", "openai/gpt-3.5-turbo"]
            ... )
            >>> print(response.choices[0].message["content"])
        """
        # Validate inputs
        validate_model_name(model)
        validate_messages(messages)
        validate_stream(stream)

        # Validate fallback models if provided
        if fallback_models:
            for i, fallback_model in enumerate(fallback_models):
                validate_model_name(fallback_model)

        # Preserve original messages for cache operations (before _process_capabilities mutates them)
        import copy
        original_messages = copy.deepcopy(messages)

        # Check cache first (use original unmutated messages)
        from . import _cache

        if _cache is not None:
            cached_response = _cache.get(model, original_messages, **kwargs)
            if cached_response is not None:
                if stream:
                    # Return simulated streaming from cached response
                    return _cache.simulate_streaming(cached_response)
                else:
                    return cached_response

        # Process fallback configuration
        fb_config = None
        if fallback_config:
            fb_config = FallbackConfig(**fallback_config)

        # Add retries by prepending the primary model to fallback_models
        # This effectively retries the primary model before trying fallbacks
        effective_fallback_models = fallback_models
        if retries > 0:
            if effective_fallback_models is None:
                effective_fallback_models = [model] * retries
            else:
                effective_fallback_models = [model] * retries + effective_fallback_models

        # Get provider with fallbacks or a regular provider
        provider, model_name = get_provider_with_fallbacks(
            primary_model=model,
            fallback_models=effective_fallback_models,
            fallback_config=fb_config,
        )

        # Process capabilities - adjust messages and kwargs based on provider support
        processed_messages, stream, processed_kwargs = cls._process_capabilities(
            provider, messages, stream, kwargs
        )

        # Call the provider's method synchronously using our safe async runner
        # This handles edge cases like Jupyter notebooks, existing event loops, etc.
        response = run_async(
            provider.create_chat_completion(
                messages=processed_messages, model=model_name, stream=stream, **processed_kwargs
            )
        )

        # Cache the response (use original unmutated messages)
        if _cache is not None:
            if stream:
                # For streaming, accumulate chunks and cache the complete response
                response = cls._accumulate_and_cache_stream(
                    response, _cache, model, original_messages, **kwargs
                )
            else:
                # For non-streaming, cache directly
                _cache.set(model, original_messages, response, **kwargs)

        return response

    @classmethod
    async def acreate(
        cls,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        fallback_models: list[str] | None = None,
        fallback_config: dict[str, Any] | None = None,
        retries: int = 0,
        **kwargs
    ) -> ChatCompletionResponse | AsyncGenerator[ChatCompletionChunk, None]:
        """
        Create a chat completion asynchronously.

        This asynchronous method creates a chat completion using the specified model.
        It supports fallback models if the primary model fails, and can retry the
        primary model before falling back. It handles both streaming and non-streaming
        responses.

        Args:
            model: Model name with provider prefix (e.g., 'openai/gpt-4')
            messages: List of messages in the conversation
            stream: Whether to stream the response
            fallback_models: Optional list of models to try if the primary model fails
            fallback_config: Optional configuration for fallback behavior
            retries: Number of times to retry the primary model before falling back (default: 0)
            **kwargs: Additional model parameters

        Returns:
            ChatCompletionResponse or a generator yielding ChatCompletionChunk objects

        Example:
            >>> response = await ChatCompletion.acreate(
            ...     model="openai/gpt-4",
            ...     messages=[
            ...         {"role": "system", "content": "You are a helpful assistant."},
            ...         {"role": "user", "content": "Hello, how are you?"}
            ...     ],
            ...     fallback_models=["anthropic/claude-3-haiku", "openai/gpt-3.5-turbo"]
            ... )
            >>> print(response.choices[0].message["content"])
        """
        # Validate inputs
        validate_model_name(model)
        validate_messages(messages)
        validate_stream(stream)

        # Validate fallback models if provided
        if fallback_models:
            for i, fallback_model in enumerate(fallback_models):
                validate_model_name(fallback_model)

        # Preserve original messages for cache operations (before _process_capabilities mutates them)
        import copy
        original_messages = copy.deepcopy(messages)

        # Check cache first (use original unmutated messages)
        from . import _cache

        if _cache is not None:
            cached_response = _cache.get(model, original_messages, **kwargs)
            if cached_response is not None:
                if stream:
                    # Return simulated streaming from cached response
                    return _cache.simulate_streaming(cached_response)
                else:
                    return cached_response

        # Process fallback configuration
        fb_config = None
        if fallback_config:
            fb_config = FallbackConfig(**fallback_config)

        # Add retries by prepending the primary model to fallback_models
        # This effectively retries the primary model before trying fallbacks
        effective_fallback_models = fallback_models
        if retries > 0:
            if effective_fallback_models is None:
                effective_fallback_models = [model] * retries
            else:
                effective_fallback_models = [model] * retries + effective_fallback_models

        # Get provider with fallbacks or a regular provider
        provider, model_name = get_provider_with_fallbacks(
            primary_model=model,
            fallback_models=effective_fallback_models,
            fallback_config=fb_config,
        )

        # Process capabilities - adjust messages and kwargs based on provider support
        processed_messages, stream, processed_kwargs = cls._process_capabilities(
            provider, messages, stream, kwargs
        )

        # Call the provider's method asynchronously
        response = await provider.create_chat_completion(
            messages=processed_messages, model=model_name, stream=stream, **processed_kwargs
        )

        # Cache the response (use original unmutated messages)
        if _cache is not None:
            if stream:
                # For streaming, accumulate chunks and cache the complete response
                response = cls._aaccumulate_and_cache_stream(
                    response, _cache, model, original_messages, **kwargs
                )
            else:
                # For non-streaming, cache directly
                _cache.set(model, original_messages, response, **kwargs)

        return response
