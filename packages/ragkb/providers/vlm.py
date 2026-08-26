"""Vision-language model providers for image understanding (schematics)."""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod

from openai import AsyncOpenAI


class VLMProvider(ABC):
    """Abstraction over multimodal backends that can describe an image."""

    @abstractmethod
    async def describe_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        """Return a textual description of an image."""


class OpenAICompatibleVLM(VLMProvider):
    """Vision via any OpenAI-compatible chat endpoint (Qwen-VL, GPT-4o, etc.)."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 120.0,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or AsyncOpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    @property
    def model(self) -> str:
        return self._model

    async def describe_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        data_uri = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                }
            ],
        )
        return response.choices[0].message.content or ""
