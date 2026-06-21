"""
LiteLLM can return assistant ``content=None`` (e.g. Gemini preview with zero completion tokens).
smolagents ``CodeAgent`` then calls ``parse_code_blobs(None, ...)``, which uses ``re.findall`` and
raises: ``TypeError: expected string or bytes-like object, got 'NoneType'``.

This subclass normalizes ``None`` to a string and optionally retries once when the first
response has no text.
"""

from __future__ import annotations

import logging
from typing import Any, Generator, List, Optional

from smolagents.models import ChatMessage, ChatMessageStreamDelta, LiteLLMModel

logger = logging.getLogger(__name__)


class NormalizedLiteLLMModel(LiteLLMModel):
    """``LiteLLMModel`` that never yields ``ChatMessage.content is None`` to agents."""

    def generate(
        self,
        messages: List[Any],
        stop_sequences: Optional[List[str]] = None,
        response_format: Optional[dict[str, str]] = None,
        tools_to_call_from: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> ChatMessage:
        for attempt in range(2):
            try:
                msg = super().generate(
                    messages,
                    stop_sequences=stop_sequences,
                    response_format=response_format,
                    tools_to_call_from=tools_to_call_from,
                    **kwargs,
                )
            except IndexError as exc:
                # Some providers occasionally return choices=[], and smolagents then crashes on choices[0].
                if attempt == 0:
                    logger.warning(
                        "Model %s returned empty choices (IndexError); retrying completion once.",
                        self.model_id,
                    )
                    continue
                raise

            if msg.content is None and attempt == 0:
                logger.warning(
                    "Model %s returned assistant content=None; retrying completion once.",
                    self.model_id,
                )
                continue

            if msg.content is None:
                logger.warning(
                    "Model %s still returned content=None; using empty string to avoid parser crash.",
                    self.model_id,
                )
                msg.content = ""
            return msg

        # Defensive fallback; loop above should either return or raise.
        logger.warning(
            "Model %s did not produce a normal response after retry; returning empty content.",
            self.model_id,
        )
        msg = ChatMessage(role="assistant", content="")
        return msg

    def generate_stream(
        self,
        messages: List[Any],
        stop_sequences: Optional[List[str]] = None,
        response_format: Optional[dict[str, str]] = None,
        tools_to_call_from: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> Generator[ChatMessageStreamDelta, None, None]:
        for delta in super().generate_stream(
            messages,
            stop_sequences=stop_sequences,
            response_format=response_format,
            tools_to_call_from=tools_to_call_from,
            **kwargs,
        ):
            if delta.content is None:
                yield ChatMessageStreamDelta(
                    content="",
                    tool_calls=delta.tool_calls,
                    token_usage=delta.token_usage,
                )
            else:
                yield delta
