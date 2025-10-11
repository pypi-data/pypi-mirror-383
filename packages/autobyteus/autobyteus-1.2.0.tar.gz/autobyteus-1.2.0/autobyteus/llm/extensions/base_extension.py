from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from autobyteus.llm.utils.messages import Message
from autobyteus.llm.utils.response_types import CompleteResponse
from autobyteus.llm.user_message import LLMUserMessage

if TYPE_CHECKING:
    from autobyteus.llm.base_llm import BaseLLM

class LLMExtension(ABC):
    def __init__(self, llm: 'BaseLLM'):
        self.llm = llm

    @abstractmethod
    async def before_invoke(
        self, user_message: LLMUserMessage, **kwargs
    ) -> None:
        """
        Called before invoking the LLM with a user message.
        """
        pass

    @abstractmethod
    async def after_invoke(
        self, user_message: LLMUserMessage, response: CompleteResponse = None, **kwargs
    ) -> None:
        """
        Called after receiving the response from the LLM.
        
        Args:
            user_message: The original user message object.
            response: Complete response including content and usage information.
            kwargs: Additional arguments.
        """
        pass

    def on_user_message_added(self, message: Message):
        pass

    def on_assistant_message_added(self, message: Message):
        pass

    async def cleanup(self) -> None:
        pass
