import os
from typing import TYPE_CHECKING, Literal, Optional
from langchain_core.language_models.chat_models import BaseChatModel

if TYPE_CHECKING:
    from geoevolve.config import GeoEvolveConfig

SourceType = Literal["OpenAI", "AzureOpenAI", "Anthropic", "Ollama", "Gemini", "Groq"]
ALLOWED_SOURCES: set[str] = set(SourceType.__args__)