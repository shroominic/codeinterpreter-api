from langchain.schema import HumanMessage, AIMessage  # type: ignore
from pydantic import BaseModel


class File(BaseModel):
    name: str
    content: bytes


class UserRequest(HumanMessage):
    text: str = ""
    files: list[File] = []


class CodeInterpreterResponse(AIMessage):
    files: list[File] = []
    final_code: str = ""
    final_output: str = ""


class CodeInput(BaseModel): 
    code: str
    

class FileInput(BaseModel): 
    filename: str
