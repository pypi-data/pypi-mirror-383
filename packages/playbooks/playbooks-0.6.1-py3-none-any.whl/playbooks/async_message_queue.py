"""
Pure async message queue implementation with event-driven message handling.

This module provides a clean, async-first message queue that replaces
timeout-based polling with pure event-driven patterns using asyncio.Condition.
"""

import asyncio
import logging
from typing import List, Callable, Optional, Any, Dict
from collections import deque
from weakref import WeakSet
import time

from playbooks.message import Message

logger = logging.getLogger(__name__)


class AsyncMessageQueue:
    """
    Event-driven message queue with zero polling.

    This implementation provides:
    - Pure event-driven message delivery using asyncio.Condition
    - Predicate-based message filtering
    - Priority message handling
    - Graceful shutdown with timeout
    - Memory-efficient message buffering
    - Message ordering guarantees

    Example:
        queue = AsyncMessageQueue()

        # Put message
        await queue.put(message)

        # Get any message
        msg = await queue.get()

        # Get message matching criteria
        msg = await queue.get(lambda m: m.sender_id == "agent-123")

        # Get multiple messages with timeout
        msgs = await queue.get_batch(predicate=None, timeout=5.0, max_messages=10)
    """

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize the async message queue.

        Args:
            max_size: Maximum number of messages to buffer (None for unlimited)
        """
        self._messages: deque[Message] = deque(maxlen=max_size)
        self._condition = asyncio.Condition()
        self._closed = False
        self._max_size = max_size
        self._waiters: WeakSet[asyncio.Task] = WeakSet()

        # Statistics
        self._total_messages = 0
        self._total_gets = 0
        self._creation_time = time.time()

    async def put(self, message: Message, priority: bool = False) -> None:
        """
        Add a message to the queue and notify waiters.

        Args:
            message: The message to add
            priority: If True, add to front of queue (high priority)

        Raises:
            RuntimeError: If queue is closed
            ValueError: If message is None
        """
        if message is None:
            raise ValueError("Message cannot be None")

        async with self._condition:
            if self._closed:
                raise RuntimeError("Cannot put message to closed queue")

            # Add message based on priority
            if priority:
                self._messages.appendleft(message)
            else:
                self._messages.append(message)

            self._total_messages += 1

            # Notify all waiters
            self._condition.notify_all()

            logger.debug(f"Message added to queue: {message.content[:50]}...")

    async def get(
        self,
        predicate: Optional[Callable[[Message], bool]] = None,
        timeout: Optional[float] = None,
    ) -> Message:
        """
        Get a message matching the predicate - pure event driven.

        Args:
            predicate: Function to test messages (None matches any message)
            timeout: Maximum time to wait for a matching message

        Returns:
            The first message matching the predicate

        Raises:
            RuntimeError: If queue is closed
            asyncio.TimeoutError: If timeout expires
            asyncio.CancelledError: If operation is cancelled
        """
        async with self._condition:
            # Track this operation
            current_task = asyncio.current_task()
            if current_task:
                self._waiters.add(current_task)

            try:
                while True:
                    if self._closed and not self._messages:
                        raise RuntimeError("Queue is closed and empty")

                    # Search for matching message
                    for i, message in enumerate(self._messages):
                        if predicate is None or predicate(message):
                            # Remove and return the message
                            found_message = self._messages[i]
                            del self._messages[i]
                            self._total_gets += 1

                            logger.debug(
                                f"Message retrieved from queue: {found_message.content[:50]}..."
                            )
                            return found_message

                    # No matching message found, wait for new ones
                    if self._closed:
                        raise RuntimeError("Queue is closed")

                    # Wait with optional timeout
                    if timeout is not None:
                        await asyncio.wait_for(self._condition.wait(), timeout=timeout)
                    else:
                        await self._condition.wait()

            except asyncio.CancelledError:
                logger.debug("Message get operation cancelled")
                raise
            finally:
                # Clean up waiter tracking
                if current_task:
                    self._waiters.discard(current_task)

    async def get_batch(
        self,
        predicate: Optional[Callable[[Message], bool]] = None,
        max_messages: int = 10,
        timeout: float = 5.0,
        min_messages: int = 1,
    ) -> List[Message]:
        """
        Get multiple messages in a batch with smart buffering.

        This method implements intelligent batching similar to the original
        _process_collected_messages logic but with pure event-driven waiting.

        Args:
            predicate: Function to test messages (None matches any)
            max_messages: Maximum messages to return in batch
            timeout: Maximum time to wait for messages
            min_messages: Minimum messages before returning (unless timeout)

        Returns:
            List of messages (may be empty if timeout and no matches)

        Raises:
            RuntimeError: If queue is closed
        """
        async with self._condition:
            if self._closed and not self._messages:
                raise RuntimeError("Queue is closed and empty")

            collected = []
            start_time = asyncio.get_event_loop().time()

            while len(collected) < max_messages:
                # Collect all currently available matching messages
                messages_found = 0
                i = 0
                while i < len(self._messages) and len(collected) < max_messages:
                    message = self._messages[i]
                    if predicate is None or predicate(message):
                        # Remove and collect the message
                        collected.append(self._messages[i])
                        del self._messages[i]
                        messages_found += 1
                    else:
                        i += 1

                # Update stats
                self._total_gets += messages_found

                # Check if we have enough messages or timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if len(collected) >= min_messages or elapsed >= timeout:
                    break

                # Check if queue is closing
                if self._closed:
                    break

                # Wait for more messages (with remaining timeout)
                remaining_timeout = timeout - elapsed
                if remaining_timeout <= 0:
                    break

                try:
                    await asyncio.wait_for(
                        self._condition.wait(), timeout=remaining_timeout
                    )
                except asyncio.TimeoutError:
                    break

            logger.debug(f"Batch retrieved {len(collected)} messages")
            return collected

    async def peek(
        self, predicate: Optional[Callable[[Message], bool]] = None
    ) -> Optional[Message]:
        """
        Look at the next matching message without removing it.

        Args:
            predicate: Function to test messages (None matches any)

        Returns:
            The first matching message, or None if no match
        """
        async with self._condition:
            for message in self._messages:
                if predicate is None or predicate(message):
                    return message
            return None

    async def remove(self, predicate: Callable[[Message], bool]) -> int:
        """
        Remove all messages matching the predicate.

        Args:
            predicate: Function to test messages for removal

        Returns:
            Number of messages removed
        """
        async with self._condition:
            if self._closed:
                raise RuntimeError("Cannot remove from closed queue")

            removed_count = 0
            i = 0
            while i < len(self._messages):
                if predicate(self._messages[i]):
                    del self._messages[i]
                    removed_count += 1
                else:
                    i += 1

            logger.debug(f"Removed {removed_count} messages from queue")
            return removed_count

    async def clear(self) -> int:
        """
        Clear all messages from the queue.

        Returns:
            Number of messages cleared
        """
        async with self._condition:
            count = len(self._messages)
            self._messages.clear()
            logger.debug(f"Cleared {count} messages from queue")
            return count

    async def close(self, timeout: float = 5.0) -> None:
        """
        Close the queue and wake all waiters.

        Args:
            timeout: Maximum time to wait for active operations to complete
        """
        async with self._condition:
            if self._closed:
                return

            self._closed = True
            # Wake up all waiters
            self._condition.notify_all()

        # Give active waiters time to complete
        if self._waiters:
            try:
                active_waiters = [task for task in self._waiters if not task.done()]
                if active_waiters:
                    await asyncio.wait_for(
                        asyncio.gather(*active_waiters, return_exceptions=True),
                        timeout=timeout,
                    )
            except asyncio.TimeoutError:
                logger.warning(
                    f"Some message queue operations did not complete within {timeout}s"
                )

        logger.debug("Message queue closed")

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        await self.close()

    @property
    def size(self) -> int:
        """Get current number of messages in queue."""
        return len(self._messages)

    @property
    def is_closed(self) -> bool:
        """Check if queue is closed."""
        return self._closed

    @property
    def is_full(self) -> bool:
        """Check if queue is at maximum capacity."""
        return self._max_size is not None and len(self._messages) >= self._max_size

    @property
    def stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        uptime = time.time() - self._creation_time
        return {
            "size": len(self._messages),
            "max_size": self._max_size,
            "total_messages": self._total_messages,
            "total_gets": self._total_gets,
            "uptime_seconds": uptime,
            "messages_per_second": self._total_messages / uptime if uptime > 0 else 0,
            "active_waiters": len(self._waiters),
            "is_closed": self._closed,
        }


class PriorityAsyncMessageQueue(AsyncMessageQueue):
    """
    Message queue with priority levels.

    Messages are organized by priority levels (0=highest, higher numbers=lower priority).
    Within each priority level, messages maintain FIFO order.
    """

    def __init__(self, max_size: Optional[int] = None, max_priority: int = 10):
        """
        Initialize priority message queue.

        Args:
            max_size: Maximum total messages across all priorities
            max_priority: Maximum priority level (0 to max_priority)
        """
        # Don't call super().__init__ to avoid creating the simple deque
        self._priority_queues: Dict[int, deque[Message]] = {
            i: deque() for i in range(max_priority + 1)
        }
        self._condition = asyncio.Condition()
        self._closed = False
        self._max_size = max_size
        self._max_priority = max_priority
        self._waiters: WeakSet[asyncio.Task] = WeakSet()

        # Statistics
        self._total_messages = 0
        self._total_gets = 0
        self._creation_time = time.time()

    async def put(self, message: Message, priority: int = 5) -> None:
        """
        Add message with specific priority.

        Args:
            message: The message to add
            priority: Priority level (0=highest priority)
        """
        if message is None:
            raise ValueError("Message cannot be None")

        if not (0 <= priority <= self._max_priority):
            raise ValueError(f"Priority must be between 0 and {self._max_priority}")

        async with self._condition:
            if self._closed:
                raise RuntimeError("Cannot put message to closed queue")

            # Check total size limit
            if self._max_size is not None and self.size >= self._max_size:
                raise RuntimeError("Queue is full")

            # Add to appropriate priority queue
            self._priority_queues[priority].append(message)
            self._total_messages += 1

            # Notify waiters
            self._condition.notify_all()

    async def get(
        self,
        predicate: Optional[Callable[[Message], bool]] = None,
        timeout: Optional[float] = None,
    ) -> Message:
        """Get highest priority message matching predicate."""
        async with self._condition:
            current_task = asyncio.current_task()
            if current_task:
                self._waiters.add(current_task)

            try:
                while True:
                    if self._closed and self.size == 0:
                        raise RuntimeError("Queue is closed and empty")

                    # Search by priority (0 = highest)
                    for priority in range(self._max_priority + 1):
                        queue = self._priority_queues[priority]
                        for i, message in enumerate(queue):
                            if predicate is None or predicate(message):
                                # Remove and return
                                found_message = queue[i]
                                del queue[i]
                                self._total_gets += 1
                                return found_message

                    # No matching message, wait
                    if self._closed:
                        raise RuntimeError("Queue is closed")

                    if timeout is not None:
                        await asyncio.wait_for(self._condition.wait(), timeout=timeout)
                    else:
                        await self._condition.wait()

            finally:
                if current_task:
                    self._waiters.discard(current_task)

    @property
    def size(self) -> int:
        """Get total number of messages across all priorities."""
        return sum(len(queue) for queue in self._priority_queues.values())

    @property
    def priority_stats(self) -> Dict[int, int]:
        """Get message count by priority level."""
        return {
            priority: len(queue)
            for priority, queue in self._priority_queues.items()
            if len(queue) > 0
        }


class MessageBuffer:
    """
    Smart message buffering with timing-based release logic.

    This class provides the intelligent buffering behavior from the original
    messaging system, but with pure async implementation.
    """

    def __init__(self, queue: AsyncMessageQueue, buffer_timeout: float = 5.0):
        """
        Initialize message buffer.

        Args:
            queue: The underlying message queue
            buffer_timeout: Maximum time to buffer messages
        """
        self.queue = queue
        self.buffer_timeout = buffer_timeout

    async def wait_for_messages(
        self, wait_for_message_from: str, timeout: Optional[float] = None
    ) -> List[Message]:
        """
        Wait for messages with smart buffering logic.

        This replicates the original WaitForMessage behavior but with
        pure event-driven implementation.

        Args:
            wait_for_message_from: Message source filter
            timeout: Maximum wait time

        Returns:
            List of collected messages
        """

        # Create predicate based on source filter
        def source_predicate(message: Message) -> bool:
            if wait_for_message_from == "*":
                return True
            elif wait_for_message_from == "human":
                return message.sender_id == "human"
            elif wait_for_message_from.startswith("meeting "):
                meeting_id = wait_for_message_from.split(" ", 1)[1]
                return message.meeting_id == meeting_id
            elif wait_for_message_from.startswith("agent "):
                agent_id = wait_for_message_from.split(" ", 1)[1]
                return message.sender_id == agent_id
            else:
                return message.sender_id == wait_for_message_from

        # For meeting messages, always wait full buffer timeout
        if wait_for_message_from.startswith("meeting "):
            min_messages = 1
            buffer_timeout = self.buffer_timeout
        else:
            # For direct messages, return immediately on first match
            min_messages = 1
            buffer_timeout = self.buffer_timeout

        return await self.queue.get_batch(
            predicate=source_predicate,
            timeout=timeout or buffer_timeout,
            min_messages=min_messages,
            max_messages=100,  # Reasonable batch limit
        )
