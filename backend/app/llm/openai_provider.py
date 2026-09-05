import json
import logging
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
import httpx
from app.core.config import settings
from app.llm.provider import LLMProvider
from app.llm.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class OpenAIProvider(LLMProvider):
    """
    Calls any OpenAI-compatible Chat Completion API with JSON mode or function calling.
    Falls back gracefully to MockLLMProvider on network/authentication failure.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.fallback = MockLLMProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}. Falling back to MockLLMProvider.")
            return self.fallback.generate(prompt, system_prompt)

    def generate_structured(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        if not self.api_key:
            return self.fallback.generate_structured(prompt, schema_cls, system_prompt)

        schema_json = json.dumps(schema_cls.model_json_schema())
        full_system = (
            f"{system_prompt or ''}\nYou are an expert university resource scheduling parser. "
            f"You MUST respond ONLY with a valid JSON object strictly matching this schema:\n{schema_json}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": full_system},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                content = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return schema_cls.model_validate(parsed)
        except Exception as e:
            logger.warning(f"OpenAI structured call failed: {e}. Falling back to MockLLMProvider.")
            return self.fallback.generate_structured(prompt, schema_cls, system_prompt)
