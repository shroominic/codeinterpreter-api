from pydantic import BaseModel


class CodeInput(BaseModel):
    code: str


class FileInput(BaseModel):
    filename: str
