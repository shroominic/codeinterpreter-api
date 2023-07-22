from pydantic import BaseSettings
from dotenv import load_dotenv
from typing import Optional

# .env file
load_dotenv(dotenv_path="./.env")


class CodeInterpreterAPISettings(BaseSettings):
    """
    CodeInterpreter API Config
    """

    VERBOSE: bool = False

    CODEBOX_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = "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"


settings = CodeInterpreterAPISettings()
