import os
from app.core.config import settings
from app.llm.provider import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAIProvider

_llm_instance: LLMProvider = None

def get_llm_provider() -> LLMProvider:
    """Returns the singleton LLM provider based on application configuration."""
    global _llm_instance
    if _llm_instance is None:
        if settings.LLM_PROVIDER.lower() == "openai" and settings.LLM_API_KEY:
            _llm_instance = OpenAIProvider(
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL
            )
        else:
            _llm_instance = MockLLMProvider()
    return _llm_instance
