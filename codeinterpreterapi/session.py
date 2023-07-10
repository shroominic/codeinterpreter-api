from codeboxapi import CodeBox
from promptkit import ChatSession


class CodeInterpreterSession():
    
    def __init__(self):
        self.chatgpt = ChatSession()
        self.codebox = CodeBox()
    
    async def _init(self):
        await self.codebox.start()
        
    async def _close(self):
        await self.codebox.stop()
    
    async def code_decision(self, user_request: str):
        # check if the user wants something that requires python code execution
        # if yes, return "code"
        # if no, return "default"
        pass
    
    async def generate_response(self, text: str, files: list[dict[str, bytes]]):  # list of "file_name" x "file_content"
        """ Generate a Code Interpreter response based on the user's input."""
        if self.code_decision() == "code":
            pass
            # plan what code to write (potentially multiple steps)
            # code = chatgpt.run(code generation template)
            # codebox.run(code)
                # on error
                    # check if package is required
                        # if yes, install package
                    # ask for analysis if the error can be fixed
                        # if yes, continue code generation
                        # if no, return AssistantResponse
                # on success
                    # check if to output files to the user
                        # if yes, return AssistantResponse with files
            # write a response based on the code execution
            # return AssistantResponse
        else:
            pass
            # return AssistantResponse
        pass

    