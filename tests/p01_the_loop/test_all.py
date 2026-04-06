from __future__ import annotations

from typing import Any

from langgraph_sdk import get_sync_client


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts)
    return str(content)


def collect_llm_reply_texts(messages: list[dict[str, Any]]) -> list[str]:
    replies: list[str] = []
    for message in messages:
        role = message.get("role") or message.get("type")
        if role not in {"assistant", "ai"}:
            continue
        replies.append(_normalize_content(message.get("content", "")))
    return replies


def main() -> list[str]:
    client = get_sync_client(url="http://localhost:8000")
    final_messages: list[dict[str, Any]] = []

    for chunk in client.runs.stream(
        None,
        "lead_agent",
        input={
            "messages": [
                {"role": "human", "content": "你好，请做个自我介绍"}
            ]
        },
        stream_mode="values",
    ):
        print(chunk.event)
        print(chunk.data)
        if isinstance(chunk.data, dict):
            messages = chunk.data.get("messages")
            if isinstance(messages, list):
                final_messages = messages

    replies = collect_llm_reply_texts(final_messages)
    print("All LLM replies:")
    for reply in replies:
        print(reply)
    return replies


if __name__ == "__main__":
    main()
