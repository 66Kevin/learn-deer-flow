from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import StructuredTool


def _current_time(timezone: str = "UTC") -> str:
    try:
        current_time = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone: {timezone}") from exc
    return f"timezone={timezone}; iso_time={current_time.isoformat()}"


current_time_tool = StructuredTool.from_function(
    func=_current_time,
    name="current_time",
    description="Return the current time in ISO format for a named timezone.",
)
