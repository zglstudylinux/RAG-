"""OpenAI-compatible LLM provider.

Covers DeepSeek / Qwen(DashScope) / Zhipu / SiliconFlow / Moonshot / OpenAI via one client.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence

from openai import AsyncOpenAI

from ragkb.providers.base import ChatResult, LLMProvider, Message


class OpenAICompatibleLLM(LLMProvider):
    """Chat completions against any OpenAI-compatible endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.2,
        timeout: float = 60.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._model = model
        self._temperature = temperature
        self._client = client or AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, messages: Sequence[Message], **kwargs: object) -> ChatResult:
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=kwargs.get("temperature", self._temperature),
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        content = response.choices[0].message.content or ""
        return ChatResult(content=content, raw=response)

    async def stream(self, messages: Sequence[Message], **kwargs: object) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            temperature=kwargs.get("temperature", self._temperature),
            messages=[{"role": m.role, "content": m.content} for m in messages],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
