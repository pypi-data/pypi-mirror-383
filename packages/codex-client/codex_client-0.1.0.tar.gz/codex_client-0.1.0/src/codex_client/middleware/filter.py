"""Logging filter that captures Codex MCP events."""

from __future__ import annotations

import asyncio
import logging

from ..event import AllEvents
from ..exceptions import MiddlewareError
from .parser import parse_event_from_message


class CodexEventFilter(logging.Filter):
    """Filter Codex MCP validation warnings while capturing event payloads."""

    def __init__(self, event_queue: "asyncio.Queue[AllEvents]") -> None:
        super().__init__()
        self._event_queue = event_queue

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records, capturing Codex events and suppressing warnings."""

        if not hasattr(record, "getMessage"):
            return True

        message = record.getMessage()

        if "Failed to validate notification" in message and "codex/event" in message:
            event = parse_event_from_message(message)
            if event is not None:
                self._queue_event(event)
            return False

        if "validation errors for ServerNotification" in message:
            return False

        return True

    def _queue_event(self, event: AllEvents) -> None:
        try:
            self._event_queue.put_nowait(event)
        except Exception as exc:
            raise MiddlewareError("failed to enqueue Codex event") from exc


__all__ = ["CodexEventFilter"]
