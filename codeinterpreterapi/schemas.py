from promptkit import AssistantResponse
from promptkit.schema import UserMessage


class UserRequest(UserMessage):
    text: str = ""
    files: list[dict[str, bytes]] = []


class CodeInterpreterResponse(AssistantResponse):
    files: list[dict[str, bytes]] = []
    final_code: str = ""
    final_output: str = ""
