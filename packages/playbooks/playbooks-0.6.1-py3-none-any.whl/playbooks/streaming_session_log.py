"""Streaming wrapper for SessionLog that broadcasts entries via callbacks."""

import asyncio
from datetime import datetime
from typing import Callable, Optional

from playbooks.session_log import SessionLog, SessionLogItem, SessionLogItemLevel
from playbooks.session_log_items import SessionLogItemBase


class StreamingSessionLog(SessionLog):
    """
    A SessionLog wrapper that streams log entries via a callback.

    This allows web servers, UIs, or other consumers to receive
    real-time updates of session log entries.
    """

    def __init__(
        self, klass: str, agent_id: str, stream_callback: Optional[Callable] = None
    ):
        super().__init__(klass, agent_id)
        self.stream_callback = stream_callback

    def set_stream_callback(self, callback: Callable):
        """Set or update the stream callback and optionally stream existing entries."""
        self.stream_callback = callback

    def append(
        self,
        item: SessionLogItem | str,
        level: SessionLogItemLevel = SessionLogItemLevel.MEDIUM,
    ):
        """Override append to stream entries to callback."""
        # Call parent append first
        super().append(item, level)

        # Stream the entry if we have a callback
        if self.stream_callback and self.log:
            # Get the last appended entry
            last_entry = self.log[-1]
            item = last_entry["item"]

            # Create streaming event data
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id,
                "agent_klass": self.klass,
                "level": level.name,
                "content": str(item),
            }

            # Add metadata if it's an enhanced SessionLogItem
            if isinstance(item, SessionLogItemBase):
                event_data["metadata"] = item.to_metadata()
                event_data["item_type"] = item.item_type
            elif hasattr(item, "__class__"):
                # For existing item types like PlaybookCall
                event_data["item_type"] = item.__class__.__name__.lower()
            else:
                event_data["item_type"] = "message"

            # Add different log representations
            if hasattr(item, "to_log_full"):
                event_data["log_full"] = item.to_log_full()
            if hasattr(item, "to_log_compact"):
                event_data["log_compact"] = item.to_log_compact()
            if hasattr(item, "to_log_minimal"):
                event_data["log_minimal"] = item.to_log_minimal()

            # Call the callback
            if asyncio.iscoroutinefunction(self.stream_callback):
                # If callback is async, create a task to run it
                asyncio.create_task(self.stream_callback(event_data))
            else:
                # If callback is sync, just call it
                self.stream_callback(event_data)

    @classmethod
    def wrap_existing(
        cls, existing_log: SessionLog, stream_callback: Optional[Callable] = None
    ) -> "StreamingSessionLog":
        """
        Wrap an existing SessionLog to add streaming capability.

        This is useful when you want to retrofit streaming onto
        an already-created SessionLog.
        """
        streaming_log = cls(existing_log.klass, existing_log.agent_id, stream_callback)
        streaming_log.log = existing_log.log
        return streaming_log
