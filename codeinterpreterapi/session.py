import uuid, base64, re
from io import BytesIO
from typing import Optional
from codeboxapi import CodeBox  # type: ignore
from codeboxapi.schema import CodeBoxOutput  # type: ignore
from langchain.tools import StructuredTool, BaseTool
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.prompts.chat import MessagesPlaceholder
from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.memory import ConversationBufferMemory

from codeinterpreterapi.schema import CodeInterpreterResponse, CodeInput, File, UserRequest
from codeinterpreterapi.config import settings
from codeinterpreterapi.chains.functions_agent import OpenAIFunctionsAgent
from codeinterpreterapi.prompts import code_interpreter_system_message
from codeinterpreterapi.callbacks import CodeCallbackHandler
from codeinterpreterapi.chains.modifications_check import get_file_modifications
from codeinterpreterapi.chains.remove_download_link import remove_download_link


class CodeInterpreterSession:
    def __init__(
        self,
        model="gpt-4",
        openai_api_key=settings.OPENAI_API_KEY,
        verbose=settings.VERBOSE,
        tools: list[BaseTool] = [],
    ) -> None:
        self.codebox = CodeBox()
        self.verbose = verbose
        self.tools: list[BaseTool] = self._tools(tools)
        self.llm: BaseChatModel = self._llm(model, openai_api_key)
        self.agent_executor: AgentExecutor = self._agent_executor()
        self.input_files: list[File] = []
        self.output_files: list[File] = []

    async def astart(self) -> None:
        await self.codebox.astart()

    def _tools(
        self, 
        additional_tools: list[BaseTool]
    ) -> list[BaseTool]:
        return additional_tools + [
            StructuredTool(
                name="python",
                description=
                # TODO: variables as context to the agent
                # TODO: current files as context to the agent
                "Input a string of code to a python interpreter (jupyter kernel). "
                "Variables are preserved between runs. ",
                func=self.run_handler,
                coroutine=self.arun_handler,
                args_schema=CodeInput,
            ),
        ]

    def _llm(
        self, 
        model: str, 
        openai_api_key: Optional[str] = None
    ) -> BaseChatModel:
        if openai_api_key is None:
            raise ValueError(
                "OpenAI API key missing. Set OPENAI_API_KEY env variable or pass `openai_api_key` to session."
            )

        return ChatOpenAI(
            temperature=0.03,
            model=model,
            openai_api_key=openai_api_key,
            max_retries=3,
            request_timeout=60 * 3,
        )  # type: ignore

    def _agent(self) -> BaseSingleActionAgent:
        return OpenAIFunctionsAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            system_message=code_interpreter_system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )

    def _agent_executor(self) -> AgentExecutor:
        return AgentExecutor.from_agent_and_tools(
            agent=self._agent(),
            callbacks=[CodeCallbackHandler(self)],
            max_iterations=9,
            tools=self.tools,
            verbose=self.verbose,
            memory=ConversationBufferMemory(memory_key="memory", return_messages=True),
        )

    async def show_code(self, code: str) -> None:
        """Callback function to show code to the user."""
        if self.verbose:
            print(code)

    def run_handler(self, code: str):
        raise NotImplementedError("Use arun_handler for now.")

    async def arun_handler(self, code: str):
        """Run code in container and send the output to the user"""
        output: CodeBoxOutput = await self.codebox.arun(code)

        if not isinstance(output.content, str):
            raise TypeError("Expected output.content to be a string.")

        if output.type == "image/png":
            filename = f"image-{uuid.uuid4()}.png"
            file_buffer = BytesIO(base64.b64decode(output.content))
            file_buffer.name = filename
            self.output_files.append(File(name=filename, content=file_buffer.read()))
            return f"Image {filename} got send to the user."

        elif output.type == "error":
            if "ModuleNotFoundError" in output.content:
                if package := re.search(
                    r"ModuleNotFoundError: No module named '(.*)'", output.content
                ):
                    await self.codebox.ainstall(package.group(1))
                    return f"{package.group(1)} was missing but got installed now. Please try again."
            else: pass
                # TODO: preanalyze error to optimize next code generation
            if self.verbose:
                print("Error:", output.content)

        elif modifications := await get_file_modifications(code, self.llm):
            for filename in modifications:
                if filename in [file.name for file in self.input_files]:
                    continue
                fileb = await self.codebox.adownload(filename)
                if not fileb.content:
                    continue
                file_buffer = BytesIO(fileb.content)
                file_buffer.name = filename
                self.output_files.append(
                    File(name=filename, content=file_buffer.read())
                )

        return output.content

    async def input_handler(self, request: UserRequest):
        if not request.files:
            return
        if not request.content:
            request.content = (
                "I uploaded, just text me back and confirm that you got the file(s)."
            )
        request.content += "\n**The user uploaded the following files: **\n"
        for file in request.files:
            self.input_files.append(file)
            request.content += f"[Attachment: {file.name}]\n"
            await self.codebox.aupload(file.name, file.content)
        request.content += "**File(s) are now available in the cwd. **\n"

    async def output_handler(self, final_response: str) -> CodeInterpreterResponse:
        """Embed images in the response"""
        for file in self.output_files:
            if str(file.name) in final_response:
                # rm ![Any](file.name) from the response
                final_response = re.sub(rf"\n\n!\[.*\]\(.*\)", "", final_response)

        if self.output_files and re.search(rf"\n\[.*\]\(.*\)", final_response):
            final_response = await remove_download_link(final_response, self.llm)

        return CodeInterpreterResponse(content=final_response, files=self.output_files)

    async def generate_response(
        self,
        user_msg: str,
        files: list[File] = [],
        detailed_error: bool = False,
    ) -> CodeInterpreterResponse:
        """Generate a Code Interpreter response based on the user's input."""
        user_request = UserRequest(content=user_msg, files=files)
        try:
            await self.input_handler(user_request)
            response = await self.agent_executor.arun(input=user_request.content)
            return await self.output_handler(response)
        except Exception as e:
            if self.verbose:
                import traceback

                traceback.print_exc()
            if detailed_error:
                return CodeInterpreterResponse(
                    content=f"Error in CodeInterpreterSession: {e.__class__.__name__}  - {e}"
                )
            else:
                return CodeInterpreterResponse(
                    content="Sorry, something went while generating your response."
                    "Please try again or restart the session."
                )

    async def is_running(self) -> bool:
        return await self.codebox.astatus() == "running"

    async def astop(self) -> None:
        await self.codebox.astop()

    async def __aenter__(self) -> "CodeInterpreterSession":
        await self.astart()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.astop()
