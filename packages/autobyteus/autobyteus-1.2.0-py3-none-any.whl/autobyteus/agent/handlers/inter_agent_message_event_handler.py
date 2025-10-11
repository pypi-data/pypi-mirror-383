# file: autobyteus/autobyteus/agent/handlers/inter_agent_message_event_handler.py
import logging
from typing import TYPE_CHECKING

from autobyteus.agent.handlers.base_event_handler import AgentEventHandler
from autobyteus.agent.events import InterAgentMessageReceivedEvent, UserMessageReceivedEvent
from autobyteus.agent.message.inter_agent_message import InterAgentMessage
from autobyteus.agent.message.agent_input_user_message import AgentInputUserMessage
from autobyteus.agent.sender_type import SenderType

if TYPE_CHECKING:
    from autobyteus.agent.context import AgentContext 
    from autobyteus.agent.events.notifiers import AgentExternalEventNotifier

logger = logging.getLogger(__name__)

class InterAgentMessageReceivedEventHandler(AgentEventHandler):
    """
    Handles InterAgentMessageReceivedEvents by formatting the InterAgentMessage
    into an AgentInputUserMessage and enqueuing a UserMessageReceivedEvent to route
    it through the main input processing pipeline.
    """

    def __init__(self):
        logger.info("InterAgentMessageReceivedEventHandler initialized.")

    async def handle(self,
                     event: InterAgentMessageReceivedEvent,
                     context: 'AgentContext') -> None:
        """
        Processes an InterAgentMessageReceivedEvent.

        Args:
            event: The InterAgentMessageReceivedEvent.
            context: The agent's composite context.
        """
        if not isinstance(event, InterAgentMessageReceivedEvent):
            logger.warning(
                f"InterAgentMessageReceivedEventHandler received an event of type {type(event).__name__} "
                f"instead of InterAgentMessageReceivedEvent. Skipping."
            )
            return

        inter_agent_msg: InterAgentMessage = event.inter_agent_message
        
        logger.info(
            f"Agent '{context.agent_id}' handling InterAgentMessageReceivedEvent from sender "
            f"'{inter_agent_msg.sender_agent_id}', type '{inter_agent_msg.message_type.value}'. "
            f"Content: '{inter_agent_msg.content}'"
        )
        
        content_for_llm = (
            f"You have received a message from another agent.\n"
            f"Sender Agent ID: {inter_agent_msg.sender_agent_id}\n"
            f"Message Type: {inter_agent_msg.message_type.value}\n"
            f"Recipient Role Name (intended for you): {inter_agent_msg.recipient_role_name}\n"
            f"--- Message Content ---\n"
            f"{inter_agent_msg.content}\n"
            f"--- End of Message Content ---\n"
            f"Please process this information and act accordingly."
        )
        
        # --- REFACTORED: Route through the main input pipeline ---
        agent_input_user_message = AgentInputUserMessage(
            content=content_for_llm,
            sender_type=SenderType.AGENT,
            metadata={
                "sender_agent_id": inter_agent_msg.sender_agent_id,
                "original_message_type": inter_agent_msg.message_type.value
            }
        )
        
        user_message_received_event = UserMessageReceivedEvent(agent_input_user_message=agent_input_user_message) 
        await context.input_event_queues.enqueue_user_message(user_message_received_event)
        
        logger.info(
            f"Agent '{context.agent_id}' processed InterAgentMessage from sender '{inter_agent_msg.sender_agent_id}' "
            f"and enqueued UserMessageReceivedEvent to route through input pipeline."
        )
