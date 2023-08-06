from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

# .env file
load_dotenv(dotenv_path="./.env")


class CodeInterpreterAPISettings(BaseSettings):
    """
    CodeInterpreter API Config
    """

    VERBOSE: bool = False

    CODEBOX_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None


settings = CodeInterpreterAPISettings()
