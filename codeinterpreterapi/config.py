from pydantic import BaseSettings
from dotenv import load_dotenv

# .env file
load_dotenv(dotenv_path="./.env")


class CodeInterpreterAPISettings(BaseSettings):
    """
    CodeInterpreter API Config
    """

    VERBOSE: bool = False

    CODEBOX_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None


settings = CodeInterpreterAPISettings()
