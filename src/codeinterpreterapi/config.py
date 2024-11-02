from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.pydantic_v1 import BaseSettings

from codeinterpreterapi.prompts import code_interpreter_system_message


class CodeInterpreterAPISettings(BaseSettings):
    """
    CodeInterpreter API Config
    """

    DEBUG: bool = False

    # Models
    OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_API_BASE: Optional[str] = None
    AZURE_API_VERSION: Optional[str] = None
    AZURE_DEPLOYMENT_NAME: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # LLM Settings
    MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.03
    DETAILED_ERROR: bool = True
    SYSTEM_MESSAGE: SystemMessage = code_interpreter_system_message
    REQUEST_TIMEOUT: int = 3 * 60
    MAX_ITERATIONS: int = 12
    MAX_RETRY: int = 3

    # Production Settings
    HISTORY_BACKEND: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379"
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # CodeBox
    CODEBOX_API_KEY: Optional[str] = None
    CUSTOM_PACKAGES: list[str] = []

    # deprecated
    VERBOSE: bool = DEBUG

    class Config:
        env_file = "./.env"
        extra = "ignore"


settings = CodeInterpreterAPISettings()
