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
Text completion functionality for OneLLM.

This module provides a Completion class that can be used to create text
completions from various providers in a manner compatible with OpenAI's API.
"""

from collections.abc import AsyncGenerator
from typing import Any

from .models import CompletionResponse
from .providers.base import get_provider_with_fallbacks
from .utils.async_helpers import run_async
from .utils.fallback import FallbackConfig
from .validators import validate_model_name, validate_prompt, validate_stream


class Completion:
    """Class for creating text completions with various providers."""

    @classmethod
    def create(
        cls,
        model: str,
        prompt: str,
        stream: bool = False,
        fallback_models: list[str] | None = None,
        fallback_config: dict | None = None,
        retries: int = 0,
        **kwargs
    ) -> CompletionResponse | AsyncGenerator[Any, None]:
        """
        Create a text completion.

        This method provides a synchronous interface for text completion requests.
        It handles model fallbacks and retries if the primary model fails.

        Args:
            model: Model name with provider prefix (e.g., 'openai/text-davinci-003')
            prompt: Text prompt to complete
            stream: Whether to stream the response
            fallback_models: Optional list of models to try if the primary model fails
            fallback_config: Optional configuration for fallback behavior
            retries: Number of times to retry the primary model before falling back (default: 0)
            **kwargs: Additional model parameters

        Returns:
            CompletionResponse or a streaming generator

        Raises:
            ValueError: If prompt is empty

        Example:
            >>> response = Completion.create(
            ...     model="openai/text-davinci-003",
            ...     prompt="Once upon a time",
            ...     max_tokens=50,
            ...     fallback_models=["anthropic/claude-instant-1", "openai/gpt-3.5-turbo-instruct"]
            ... )
            >>> print(response.choices[0].text)
        """
        # Validate inputs
        validate_model_name(model)
        validate_prompt(prompt)
        validate_stream(stream)

        # Validate fallback models if provided
        if fallback_models:
            for fallback_model in fallback_models:
                validate_model_name(fallback_model)

        # Process fallback configuration
        fb_config = None
        if fallback_config:
            fb_config = FallbackConfig(**fallback_config)

        # Add retries by prepending the primary model to fallback_models
        # This effectively tries the primary model multiple times before moving to fallbacks
        effective_fallback_models = fallback_models
        if retries > 0:
            if effective_fallback_models is None:
                # If no fallback models were provided, create a list with the primary model repeated
                effective_fallback_models = [model] * retries
            else:
                # Prepend retries of the primary model to the fallback models list
                effective_fallback_models = [model] * retries + effective_fallback_models

        # Get provider with fallbacks or a regular provider
        # This returns both the provider instance and the specific model name to use
        provider, model_name = get_provider_with_fallbacks(
            primary_model=model,
            fallback_models=effective_fallback_models,
            fallback_config=fb_config,
        )

        # Call the provider's method synchronously using our safe async runner
        # This handles edge cases like Jupyter notebooks, existing event loops, etc.
        return run_async(
            provider.create_completion(
                prompt=prompt, model=model_name, stream=stream, **kwargs
            )
        )

    @classmethod
    async def acreate(
        cls,
        model: str,
        prompt: str,
        stream: bool = False,
        fallback_models: list[str] | None = None,
        fallback_config: dict | None = None,
        retries: int = 0,
        **kwargs
    ) -> CompletionResponse | AsyncGenerator[Any, None]:
        """
        Create a text completion asynchronously.

        This method provides an asynchronous interface for text completion requests.
        It's designed to be used with async/await syntax in asynchronous code.
        Like the synchronous version, it handles model fallbacks and retries.

        Args:
            model: Model name with provider prefix (e.g., 'openai/text-davinci-003')
            prompt: Text prompt to complete
            stream: Whether to stream the response
            fallback_models: Optional list of models to try if the primary model fails
            fallback_config: Optional configuration for fallback behavior
            retries: Number of times to retry the primary model before falling back (default: 0)
            **kwargs: Additional model parameters

        Returns:
            CompletionResponse or a streaming generator

        Raises:
            ValueError: If prompt is empty

        Example:
            >>> response = await Completion.acreate(
            ...     model="openai/text-davinci-003",
            ...     prompt="Once upon a time",
            ...     max_tokens=50,
            ...     fallback_models=["anthropic/claude-instant-1", "openai/gpt-3.5-turbo-instruct"]
            ... )
            >>> print(response.choices[0].text)
        """
        # Validate inputs
        validate_model_name(model)
        validate_prompt(prompt)
        validate_stream(stream)

        # Validate fallback models if provided
        if fallback_models:
            for fallback_model in fallback_models:
                validate_model_name(fallback_model)

        # Process fallback configuration
        fb_config = None
        if fallback_config:
            fb_config = FallbackConfig(**fallback_config)

        # Add retries by prepending the primary model to fallback_models
        # This works the same way as in the synchronous version
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

        # Call the provider's method asynchronously
        # Since this method is already async, we can directly await the result
        return await provider.create_completion(
            prompt=prompt, model=model_name, stream=stream, **kwargs
        )
