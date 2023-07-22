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
    OPENAI_API_KEY: Optional[str] = None


settings = CodeInterpreterAPISettings()
