from langchain.schema import HumanMessage, AIMessage  # type: ignore
from .file import File


class UserRequest(HumanMessage):
    files: list[File] = []

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"UserRequest(content={self.content}, files={self.files})"


class CodeInterpreterResponse(AIMessage):
    files: list[File] = []
    # final_code: str = ""  TODO: implement
    # final_output: str = ""  TODO: implement

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"CodeInterpreterResponse(content={self.content}, files={self.files})"
