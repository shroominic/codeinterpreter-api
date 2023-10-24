# Settings

## Settings Class Overview

The configuration is defined in a class named `CodeInterpreterAPISettings`, which inherits from Pydantic's `BaseSettings` class.

`codeinterpreterapi/config.py`
```python
class CodeInterpreterAPISettings(BaseSettings):
...
```

## Setting Descriptions

### Debug Settings

- `DEBUG: bool = False`
Enables or disables the debug mode.

### API Keys

- `OPENAI_API_KEY: Optional[str] = None`
API key for the OpenAI service.

- `AZURE_API_KEY: Optional[str] = None`
API key for the Azure service.

- `AZURE_API_BASE: Optional[str] = None`
Base URL for Azure API.

- `AZURE_API_VERSION: Optional[str] = None`
API version for Azure service.

- `AZURE_DEPLOYMENT_NAME: Optional[str] = None`
Deployment name for Azure service.

- `ANTHROPIC_API_KEY: Optional[SecretStr] = None`
API key for the Anthropic service, stored securely.

### LLM Settings

- `MODEL: str = "gpt-3.5-turbo"`
The language model to be used.

- `TEMPERATURE: float = 0.03`
Controls randomness in the model's output.

- `DETAILED_ERROR: bool = True`
Enables or disables detailed error messages.

- `SYSTEM_MESSAGE: SystemMessage = code_interpreter_system_message`
Sets the default system message

- `REQUEST_TIMEOUT: int = 3 * 60`
API request timeout in seconds.

- `MAX_ITERATIONS: int = 12`
Maximum number of iterations for certain operations.

- `MAX_RETRY: int = 3`
Maximum number of API request retries.

### Production Settings

- `HISTORY_BACKEND: Optional[str] = None`
Specifies the history backend to be used.

- `REDIS_URL: str = "redis://localhost:6379"`
URL for Redis server.

- `POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"`
URL for PostgreSQL server.

### CodeBox

- `CODEBOX_API_KEY: Optional[str] = None`
API key for the CodeBox service.

- `CUSTOM_PACKAGES: list[str] = []`
List of custom Python packages to be used.

### Deprecated

- `VERBOSE: bool = DEBUG`
This setting is deprecated and should not be used. It defaults to the value of `DEBUG`.
