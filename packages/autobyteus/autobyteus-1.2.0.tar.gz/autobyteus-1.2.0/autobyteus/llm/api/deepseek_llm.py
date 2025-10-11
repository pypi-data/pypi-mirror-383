import logging
from typing import Optional
from autobyteus.llm.models import LLMModel
from autobyteus.llm.utils.llm_config import LLMConfig
from autobyteus.llm.api.openai_compatible_llm import OpenAICompatibleLLM

logger = logging.getLogger(__name__)

class DeepSeekLLM(OpenAICompatibleLLM):
    def __init__(self, model: LLMModel = None, llm_config: LLMConfig = None):
        # Provide defaults if not specified
        if model is None:
            model = LLMModel['deepseek-chat']
        if llm_config is None:
            llm_config = LLMConfig()
            
        super().__init__(
            model=model,
            llm_config=llm_config,
            api_key_env_var="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com"
        )
        logger.info(f"DeepSeekLLM initialized with model: {self.model}")

    async def cleanup(self):
        await super().cleanup()
