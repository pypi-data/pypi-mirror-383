from abc import ABC, ABCMeta
from typing import TYPE_CHECKING, Any, Dict

from playbooks.debug_logger import debug
from playbooks.events import AgentPausedEvent
from playbooks.utils.spec_utils import SpecUtils

from ..llm_messages import AgentCommunicationLLMMessage
from .messaging_mixin import MessagingMixin

if TYPE_CHECKING:
    from src.playbooks.program import Program


class BaseAgentMeta(ABCMeta):
    """Meta class for BaseAgent."""

    def should_create_instance_at_start(self) -> bool:
        """Whether to create an instance of the agent at start.

        Override in subclasses to control whether to create an instance at start.
        """
        return False


class BaseAgent(MessagingMixin, ABC, metaclass=BaseAgentMeta):
    """
    Base class for all agent implementations.

    Agents define behavior - what they do, their methods, and internal state.
    The runtime (Program) decides when and where they run.
    """

    def __init__(
        self,
        agent_id: str,
        program: "Program",
        source_line_number: int = None,
        source_file_path: str = None,
        **kwargs,
    ):
        """Initialize a new BaseAgent."""
        super().__init__()
        self.klass = self.__class__.klass
        self.description = self.__class__.description
        self.metadata = self.__class__.metadata.copy()

        self.id = agent_id
        self.kwargs = kwargs
        self.program = program

        # Source tracking
        self.source_line_number = source_line_number
        self.source_file_path = source_file_path

        # Debug context
        self._debug_thread_id: int = None
        self.paused: str = None

    async def begin(self):
        """Agent startup logic. Override in subclasses."""
        pass

    async def initialize(self):
        """Agent initialization logic. Override in subclasses."""
        pass

    # Built-in playbook methods
    async def Say(self, target: str, message: str, already_streamed: bool = False):
        resolved_target = self.resolve_target(target, allow_fallback=True)

        # Handle meeting targets with broadcasting
        if SpecUtils.is_meeting_spec(resolved_target):
            meeting_id = SpecUtils.extract_meeting_id(resolved_target)
            if (
                hasattr(self, "state")
                and hasattr(self.state, "owned_meetings")
                and meeting_id in self.state.owned_meetings
            ):
                debug(
                    f"{str(self)}: Broadcasting to meeting {meeting_id} as owner: {message}"
                )
                await self.meeting_manager.broadcast_to_meeting_as_owner(
                    meeting_id, message
                )
            elif (
                hasattr(self, "state")
                and hasattr(self.state, "joined_meetings")
                and meeting_id in self.state.joined_meetings
            ):
                debug(
                    f"{str(self)}: Broadcasting to meeting {meeting_id} as participant: {message}"
                )
                await self.meeting_manager.broadcast_to_meeting_as_participant(
                    meeting_id, message
                )
            else:
                # Error: not in this meeting
                debug(f"{str(self)}: state {self.state.joined_meetings}")
                debug(
                    f"{str(self)}: Cannot broadcast to meeting {meeting_id} - not a participant"
                )
                self.state.session_log.append(
                    f"Cannot broadcast to meeting {meeting_id} - not a participant"
                )
            return

        # Track last message target (only for 1:1 messages, not meetings)
        if not (
            SpecUtils.is_meeting_spec(resolved_target) or resolved_target == "human"
        ):
            self.state.last_message_target = resolved_target

        if not already_streamed and resolved_target == "human":
            await self.start_streaming_say()
            await self.stream_say_update(message)
            await self.complete_streaming_say()

        await self.SendMessage(resolved_target, message)

    async def SendMessage(self, target_agent_id: str, message: str):
        """Send a message to another agent."""
        if not self.program:
            return

        # Add to current frame context if available
        if hasattr(self, "state") and self.state.call_stack.peek():
            current_frame = self.state.call_stack.peek()
            if current_frame.playbook == "Say":
                current_frame = self.state.call_stack.frames[-2]
            target_agent = self.program.agents_by_id.get(target_agent_id)
            target_name = (
                str(target_agent)
                if target_agent
                else self.unknown_agent_str(target_agent_id)
            )
            agent_comm_msg = AgentCommunicationLLMMessage(
                f"I {str(self)} sent message to {target_name}: {message}",
                sender_agent=self.klass,
                target_agent=target_name,
            )
            current_frame.add_llm_message(agent_comm_msg)

        # Route through program runtime
        await self.program.route_message(
            sender_id=self.id,
            sender_klass=self.klass,
            receiver_spec=target_agent_id,
            message=message,
        )

    async def start_streaming_say(self, recipient=None):
        """Start displaying a streaming Say() message. Override in subclasses."""
        pass

    async def stream_say_update(self, content: str):
        """Add content to the current streaming Say() message. Override in subclasses."""
        pass

    async def complete_streaming_say(self):
        """Complete the current streaming Say() message. Override in subclasses."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {**self.kwargs, "type": self.klass, "agent_id": self.id}

    def get_debug_thread_id(self) -> int:
        """Get the debug thread ID for this agent."""
        return self._debug_thread_id

    def set_debug_thread_id(self, thread_id: int) -> None:
        """Set the debug thread ID for this agent."""
        self._debug_thread_id = thread_id

    def emit_agent_paused_event(
        self, reason: str = "pause", source_line_number: int = 0
    ) -> None:
        """Emit an agent paused event for debugging."""
        if (
            self.program
            and hasattr(self.program, "event_bus")
            and self.program.event_bus
        ):
            event = AgentPausedEvent(
                session_id="",
                agent_id=self.id,
                reason=reason,
                source_line_number=source_line_number,
            )
            self.program.event_bus.publish(event)

    def emit_agent_resumed_event(self) -> None:
        """Emit an agent resumed event for debugging."""
        if (
            self.program
            and hasattr(self.program, "event_bus")
            and self.program.event_bus
        ):
            from playbooks.events import AgentResumedEvent

            event = AgentResumedEvent(
                session_id="",
                agent_id=self.id,
            )
            self.program.event_bus.publish(event)
