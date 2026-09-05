from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates raw text response."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema_cls: Type[T], system_prompt: Optional[str] = None) -> T:
        """Generates structured Pydantic object validated against schema_cls."""
        pass
