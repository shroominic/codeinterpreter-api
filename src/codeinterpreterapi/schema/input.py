from langchain.pydantic_v1 import BaseModel


class CodeInput(BaseModel):
    code: str


class FileInput(BaseModel):
    filename: str
