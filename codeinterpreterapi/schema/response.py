from langchain.schema import AIMessage, HumanMessage  # type: ignore

from .file import File


class UserRequest(HumanMessage):
    files: list[File] = []

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"UserRequest(content={self.content}, files={self.files})"


class CodeInterpreterResponse(AIMessage):
    """
    Response from the code interpreter agent.

    files: list of files to be sent to the user (File )
    code_log: list[tuple[str, str]] = []
    """

    files: list[File] = []
    code_log: list[tuple[str, str]] = []

    def show(self):
        print("AI: ", self.content)
        for file in self.files:
            print("File: ", file.name)
            file.show_image()

    def __str__(self):
        return self.content

    def __repr__(self):
        return f"CodeInterpreterResponse(content={self.content}, files={self.files})"
