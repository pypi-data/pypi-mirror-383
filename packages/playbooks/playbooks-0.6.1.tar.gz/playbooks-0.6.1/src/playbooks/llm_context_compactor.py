"""LLM Context Compaction for managing growing message context in playbooks."""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from playbooks.llm_messages import (
    AssistantResponseLLMMessage,
    LLMMessage,
    UserInputLLMMessage,
)


@dataclass
class CompactionConfig:
    """Configuration for LLM context compaction."""

    # Core strategy parameters
    min_preserved_assistant_messages: int = (
        None  # Always keep last N assistant messages
    )
    batch_size: int = None  # Compact in batches of N

    # Feature toggles
    enabled: bool = None  # Master enable/disable

    def __post_init__(self):
        """Initialize from environment variables if values not provided."""
        if self.enabled is None:
            self.enabled = os.getenv("LLM_COMPACTION_ENABLED", "true").lower() == "true"

        if self.min_preserved_assistant_messages is None:
            self.min_preserved_assistant_messages = int(
                os.getenv("LLM_COMPACTION_MIN_PRESERVED_ASSISTANT_MESSAGES", "1")
            )

        if self.batch_size is None:
            self.batch_size = int(os.getenv("LLM_COMPACTION_BATCH_SIZE", "3"))


class LLMContextCompactor:
    """Handles progressive compaction of LLM messages."""

    def __init__(self, config: Optional[CompactionConfig] = None):
        self.config = config or CompactionConfig()

    def compact_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Main entry point for message compaction - returns LLM API format."""
        if not self.config.enabled or len(messages) == 0:
            return [msg.to_full_message() for msg in messages]

        # Walk backwards to find last safe (uncompacted) assistant message
        assistant_count = 0
        safe_assistant_index = -1
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], AssistantResponseLLMMessage):
                assistant_count += 1
                if assistant_count >= self.config.min_preserved_assistant_messages:
                    safe_assistant_index = i
                    break

        # If no safe assistant message found, return all messages as full
        if safe_assistant_index == -1:
            return [msg.to_full_message() for msg in messages]

        # Find user message that resulted in assistant response at safe_assistant_index
        # This user message is the one that came before the safe assistant message
        safe_user_index = -1
        for i in range(safe_assistant_index - 1, -1, -1):
            if isinstance(messages[i], UserInputLLMMessage):
                safe_user_index = i
                break

        if safe_user_index == -1:
            # If no safe user message found, compact all messages before the safe assistant message
            safe_index = safe_assistant_index
        else:
            # If safe user message found, make sure it is not compacted
            safe_index = safe_user_index

        # All messages before safe_index are compacted
        result = []
        for i, msg in enumerate(messages):
            if i < safe_index:
                compact_message = msg.to_compact_message()
                if compact_message:
                    result.append(compact_message)
            else:
                result.append(msg.to_full_message())

        return result


# Convenience function for easy integration
def compact_llm_messages(
    messages: List[LLMMessage], config: Optional[CompactionConfig] = None
) -> List[Dict[str, Any]]:
    """Compact a list of LLM messages using the default compactor.

    Args:
        messages: List of LLM messages to compact
        config: Optional compaction configuration

    Returns:
        List of compacted messages in LLM API format
    """
    compactor = LLMContextCompactor(config)
    return compactor.compact_messages(messages)
