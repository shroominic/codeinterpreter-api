from pydantic import BaseSettings
from dotenv import load_dotenv

# .env file
load_dotenv()


class CodeInterpreterAPISettings(BaseSettings):
    """
    CodeInterpreter API Config
    """
    CODEBOX_API_KEY: str = None
    CODEBOX_VERBOSE: bool = False
    
    OPENAI_API_KEY: str = ""
    

settings = CodeInterpreterAPISettings()
