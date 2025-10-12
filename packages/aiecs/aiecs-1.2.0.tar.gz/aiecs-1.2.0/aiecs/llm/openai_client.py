import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from aiecs.llm.base_client import BaseLLMClient, LLMMessage, LLMResponse, ProviderNotAvailableError, RateLimitError
from aiecs.config.config import get_settings

logger = logging.getLogger(__name__)

class OpenAIClient(BaseLLMClient):
    """OpenAI provider client"""

    def __init__(self):
        super().__init__("OpenAI")
        self.settings = get_settings()
        self._client: Optional[AsyncOpenAI] = None

        # Token cost estimates (USD per 1K tokens)
        self.token_costs = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        }

    def _get_client(self) -> AsyncOpenAI:
        """Lazy initialization of OpenAI client"""
        if not self._client:
            if not self.settings.openai_api_key:
                raise ProviderNotAvailableError("OpenAI API key not configured")
            self._client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, RateLimitError))
    )
    async def generate_text(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using OpenAI API"""
        client = self._get_client()
        model = model or "gpt-4-turbo"

        # Convert to OpenAI message format
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            # Estimate cost
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            cost = self._estimate_cost(model, input_tokens, output_tokens, self.token_costs)

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=model,
                tokens_used=tokens_used,
                cost_estimate=cost
            )

        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
            raise

    async def stream_text(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text using OpenAI API"""
        client = self._get_client()
        model = model or "gpt-4-turbo"

        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        if self._client:
            await self._client.close()
            self._client = None
