"""Clean semantic LLM message types with minimal, maintainable design."""

from typing import Any, Dict, Optional

from playbooks.enums import LLMMessageRole, LLMMessageType

from .base import LLMMessage

# Core semantic message types - minimal set covering all use cases


class SystemPromptLLMMessage(LLMMessage):
    """System prompts and instructions - cached by default."""

    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.SYSTEM,
            type=LLMMessageType.SYSTEM_PROMPT,
            cached=True,
        )


class UserInputLLMMessage(LLMMessage):
    """User inputs and instructions - not cached by default."""

    def __init__(self, content: str, cached: bool = False) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.USER_INPUT,
            cached=cached,
        )

    def to_compact_message(self) -> Optional[Dict[str, Any]]:
        """Remove user inputs during compaction."""
        return None


class AssistantResponseLLMMessage(LLMMessage):
    """LLM responses - cached by default for conversation context."""

    def __init__(self, content: str, cached: bool = True) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.ASSISTANT,
            type=LLMMessageType.ASSISTANT_RESPONSE,
            cached=cached,
        )

    def to_compact_message(self) -> Dict[str, Any]:
        """Use first line that begins with 'recap -' for compaction."""
        lines = self.content.split("\n")

        # We don't want to confuse LLM with a partial assistant response
        # so we use the user role for the compacted message
        compact_message_role = LLMMessageRole.USER

        # Find line that begins with 'recap -'
        recap_line = next(
            (line.strip() for line in lines if line.strip().startswith("recap -")), None
        )
        if recap_line:
            return {
                "role": compact_message_role,
                "content": recap_line.replace("recap -", "").strip(),
            }

        # If no recap line found, use first line
        first_line = lines[0].strip() if lines else ""
        return {"role": compact_message_role, "content": first_line}


class PlaybookImplementationLLMMessage(LLMMessage):
    """Playbook markdown implementation - cached for performance."""

    def __init__(self, content: str, playbook_name: str) -> None:
        self.playbook_name = self._validate_string_param(playbook_name, "playbook_name")

        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.PLAYBOOK_IMPLEMENTATION,
            cached=True,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return super().__eq__(other) and self.playbook_name == other.playbook_name

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.playbook_name,
            )
        )


class ExecutionResultLLMMessage(LLMMessage):
    """Playbook execution results - not cached as they're context-specific."""

    def __init__(self, content: str, playbook_name: str, success: bool = True) -> None:
        self.playbook_name = self._validate_string_param(playbook_name, "playbook_name")
        if not isinstance(success, bool):
            raise TypeError(f"success must be a boolean, got {type(success).__name__}")
        self.success = success

        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.EXECUTION_RESULT,
            cached=False,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return (
            super().__eq__(other)
            and self.playbook_name == other.playbook_name
            and self.success == other.success
        )

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.playbook_name,
                self.success,
            )
        )


class AgentCommunicationLLMMessage(LLMMessage):
    """Inter-agent communications - not cached as they're event-specific."""

    def __init__(self, content: str, sender_agent: str, target_agent: str) -> None:
        self.sender_agent = self._validate_string_param(sender_agent, "sender_agent")
        self.target_agent = self._validate_string_param(target_agent, "target_agent")

        # Note: sender_agent can be the same as target_agent in meeting contexts
        # or when an agent is processing its own messages

        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.AGENT_COMMUNICATION,
            cached=False,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return (
            super().__eq__(other)
            and self.sender_agent == other.sender_agent
            and self.target_agent == other.target_agent
        )

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.sender_agent,
                self.target_agent,
            )
        )


class MeetingLLMMessage(LLMMessage):
    """Meeting-related communications - not cached as they're event-specific."""

    def __init__(self, content: str, meeting_id: str) -> None:
        self.meeting_id = self._validate_string_param(meeting_id, "meeting_id")

        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.MEETING_MESSAGE,
            cached=False,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return super().__eq__(other) and self.meeting_id == other.meeting_id

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.meeting_id,
            )
        )


class TriggerInstructionsLLMMessage(LLMMessage):
    """Playbook trigger instructions - cached for performance."""

    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.TRIGGER_INSTRUCTIONS,
            cached=True,
        )


class AgentInfoLLMMessage(LLMMessage):
    """Current agent information - cached as it doesn't change often."""

    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.AGENT_INFO,
            cached=True,
        )


class OtherAgentInfoLLMMessage(LLMMessage):
    """Other available agents information - cached as it doesn't change often."""

    def __init__(self, content: str) -> None:
        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.OTHER_AGENT_INFO,
            cached=True,
        )


class FileLoadLLMMessage(LLMMessage):
    """File content loading - not cached as files may change."""

    def __init__(self, content: str, file_path: str) -> None:
        self.file_path = self._validate_string_param(file_path, "file_path")
        # Note: Content size validation is now handled by base class

        super().__init__(
            content=content,
            role=LLMMessageRole.USER,
            type=LLMMessageType.FILE_LOAD,
            cached=False,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return super().__eq__(other) and self.file_path == other.file_path

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.file_path,
            )
        )


class SessionLogLLMMessage(LLMMessage):
    """Session logging and status updates - not cached."""

    def __init__(self, content: str, log_level: str = "INFO") -> None:
        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARN", "ERROR", "FATAL"}
        if not isinstance(log_level, str):
            raise TypeError(
                f"log_level must be a string, got {type(log_level).__name__}"
            )
        if log_level not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, got {log_level!r}"
            )
        self.log_level = log_level

        super().__init__(
            content=content,
            role=LLMMessageRole.SYSTEM,  # Fixed: logs are system-level information
            type=LLMMessageType.SESSION_LOG,
            cached=False,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality including custom attributes."""
        if not isinstance(other, self.__class__):
            return False
        return super().__eq__(other) and self.log_level == other.log_level

    def __hash__(self) -> int:
        """Hash including custom attributes."""
        return hash(
            (
                self.__class__.__name__,
                self.content,
                self.role,
                self.type,
                self.cached,
                self.log_level,
            )
        )
