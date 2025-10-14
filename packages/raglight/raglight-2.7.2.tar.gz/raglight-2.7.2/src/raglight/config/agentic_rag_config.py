from dataclasses import dataclass, field

from mcp import StdioServerParameters
from ..config.settings import Settings
from typing import List
from ..models.data_source_model import DataSource


@dataclass(kw_only=True)
class AgenticRAGConfig:
    api_key: str = field(default="")
    api_base: str = field(default=None)
    provider: str = field(default=Settings.OLLAMA.lower())
    model: str = field(default=Settings.DEFAULT_LLM)
    num_ctx: int = field(default=8192)
    k: int = field(default=5)
    mcp_config: List[StdioServerParameters] = field(default=None)
    verbosity_level: int = field(default=2)
    max_steps: int = field(default=4)
    system_prompt: str = field(default=Settings.DEFAULT_AGENT_PROMPT)
    knowledge_base: List[DataSource] = field(default=None)
    ignore_folders: list = field(
        default_factory=lambda: list(Settings.DEFAULT_IGNORE_FOLDERS)
    )


@dataclass(kw_only=True)
class SimpleAgenticRAGConfig:
    api_key: str = field(default="")
    api_base: str = field(default=None)
    provider: str = field(default=Settings.OLLAMA.lower())
    mcp_config: List[StdioServerParameters] = field(default=None)
    model: str = field(default=Settings.DEFAULT_LLM)
    num_ctx: int = field(default=8192)
    k: int = field(default=2)
    verbosity_level: int = field(default=2)
    max_steps: int = field(default=4)
    system_prompt: str = field(default=Settings.DEFAULT_AGENT_PROMPT)
    ignore_folders: list = field(
        default_factory=lambda: list(Settings.DEFAULT_IGNORE_FOLDERS)
    )
