from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FixedResponseChatModel:
    """Small local chat model used by tests and smoke examples."""

    model: str
    response_text: str

    def invoke(self, messages: list[dict[str, Any]] | None = None, system_prompt: str | None = None) -> dict[str, str]:
        return {
            "role": "assistant",
            "content": self.response_text,
        }

