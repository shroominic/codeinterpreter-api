import base64
import re
import traceback
from io import BytesIO
from os import getenv
from typing import Optional
from uuid import UUID, uuid4

from codeboxapi import CodeBox  # type: ignore
from codeboxapi.schema import CodeBoxOutput  # type: ignore
from langchain.agents import (
    AgentExecutor,
    BaseSingleActionAgent,
    ConversationalAgent,
    ConversationalChatAgent,
)
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import AzureChatOpenAI, ChatAnthropic, ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import (
    ChatMessageHistory,
    PostgresChatMessageHistory,
    RedisChatMessageHistory,
)
from langchain.prompts.chat import MessagesPlaceholder
from langchain.schema import BaseChatMessageHistory, SystemMessage
from langchain.tools import BaseTool, StructuredTool

from codeinterpreterapi.agents import OpenAIFunctionsAgent
from codeinterpreterapi.chains import (
    aget_file_modifications,
    aremove_download_link,
    get_file_modifications,
    remove_download_link,
)
from codeinterpreterapi.chat_history import CodeBoxChatMessageHistory
from codeinterpreterapi.config import settings
from codeinterpreterapi.parser import CodeAgentOutputParser, CodeChatAgentOutputParser
from codeinterpreterapi.prompts import code_interpreter_system_message
from codeinterpreterapi.schema import (
    CodeInput,
    CodeInterpreterResponse,
    File,
    SessionStatus,
    UserRequest,
)


class CodeInterpreterSession:
    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        system_message: SystemMessage = code_interpreter_system_message,
        max_iterations: int = 9,
        additional_tools: list[BaseTool] = [],
        **kwargs,
    ) -> None:
        self.codebox = CodeBox()
        self.verbose = kwargs.get("verbose", settings.VERBOSE)
        self.tools: list[BaseTool] = self._tools(additional_tools)
        self.llm: BaseLanguageModel = llm or self._choose_llm(**kwargs)
        self.max_iterations = max_iterations
        self.system_message = system_message
        self.agent_executor: Optional[AgentExecutor] = None
        self.input_files: list[File] = []
        self.output_files: list[File] = []
        self.code_log: list[tuple[str, str]] = []

    @classmethod
    def from_id(cls, session_id: UUID, **kwargs) -> "CodeInterpreterSession":
        session = cls(**kwargs)
        session.codebox = CodeBox.from_id(session_id)
        session.agent_executor = session._agent_executor()
        return session

    @property
    def session_id(self) -> Optional[UUID]:
        return self.codebox.session_id

    def start(self) -> SessionStatus:
        status = SessionStatus.from_codebox_status(self.codebox.start())
        self.agent_executor = self._agent_executor()
        return status

    async def astart(self) -> SessionStatus:
        status = SessionStatus.from_codebox_status(await self.codebox.astart())
        self.agent_executor = self._agent_executor()
        return status

    def _tools(self, additional_tools: list[BaseTool]) -> list[BaseTool]:
        return additional_tools + [
            StructuredTool(
                name="python",
                description="Input a string of code to a ipython interpreter. "
                "Write the entire code in a single string. This string can "
                "be really long, so you can use the `;` character to split lines. "
                "Variables are preserved between runs. ",
                func=self._run_handler,
                coroutine=self._arun_handler,
                args_schema=CodeInput,  # type: ignore
            ),
        ]

    def _choose_llm(
        self, model: str = "gpt-4", openai_api_key: Optional[str] = None, **kwargs
    ) -> BaseChatModel:
        if "gpt" in model:
            openai_api_key = (
                openai_api_key
                or settings.OPENAI_API_KEY
                or getenv("OPENAI_API_KEY", None)
            )
            if openai_api_key is None:
                raise ValueError(
                    "OpenAI API key missing. Set OPENAI_API_KEY env variable "
                    "or pass `openai_api_key` to session."
                )
            openai_api_version = getenv("OPENAI_API_VERSION")
            openai_api_base = getenv("OPENAI_API_BASE")
            deployment_name = getenv("DEPLOYMENT_NAME")
            openapi_type = getenv("OPENAI_API_TYPE")
            if (
                openapi_type == "azure"
                and openai_api_version
                and openai_api_base
                and deployment_name
            ):
                return AzureChatOpenAI(
                    temperature=0.03,
                    openai_api_base=openai_api_base,
                    openai_api_version=openai_api_version,
                    deployment_name=deployment_name,
                    openai_api_key=openai_api_key,
                    max_retries=3,
                    request_timeout=60 * 3,
                )  # type: ignore
            else:
                return ChatOpenAI(
                    temperature=0.03,
                    model=model,
                    openai_api_key=openai_api_key,
                    max_retries=3,
                    request_timeout=60 * 3,
                )  # type: ignore
        elif "claude" in model:
            return ChatAnthropic(model=model)
        else:
            raise ValueError(f"Unknown model: {model} (expected gpt or claude model)")

    def _choose_agent(self) -> BaseSingleActionAgent:
        return (
            OpenAIFunctionsAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                system_message=self.system_message,
                extra_prompt_messages=[
                    MessagesPlaceholder(variable_name="chat_history")
                ],
            )
            if isinstance(self.llm, ChatOpenAI)
            else ConversationalChatAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                system_message=code_interpreter_system_message.content,
                output_parser=CodeChatAgentOutputParser(self.llm),
            )
            if isinstance(self.llm, BaseChatModel)
            else ConversationalAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                prefix=code_interpreter_system_message.content,
                output_parser=CodeAgentOutputParser(),
            )
        )

    def _history_backend(self) -> BaseChatMessageHistory:
        return (
            CodeBoxChatMessageHistory(codebox=self.codebox)
            if settings.HISTORY_BACKEND == "codebox"
            else RedisChatMessageHistory(
                session_id=str(self.session_id),
                url=settings.REDIS_URL,
            )
            if settings.HISTORY_BACKEND == "redis"
            else PostgresChatMessageHistory(
                session_id=str(self.session_id),
                connection_string=settings.POSTGRES_URL,
            )
            if settings.HISTORY_BACKEND == "postgres"
            else ChatMessageHistory()
        )

    def _agent_executor(self) -> AgentExecutor:
        return AgentExecutor.from_agent_and_tools(
            agent=self._choose_agent(),
            max_iterations=self.max_iterations,
            tools=self.tools,
            verbose=self.verbose,
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                chat_memory=self._history_backend(),
            ),
        )

    def show_code(self, code: str) -> None:
        if self.verbose:
            print(code)

    async def ashow_code(self, code: str) -> None:
        """Callback function to show code to the user."""
        if self.verbose:
            print(code)

    def _run_handler(self, code: str):
        """Run code in container and send the output to the user"""
        self.show_code(code)
        output: CodeBoxOutput = self.codebox.run(code)
        self.code_log.append((code, output.content))

        if not isinstance(output.content, str):
            raise TypeError("Expected output.content to be a string.")

        if output.type == "image/png":
            filename = f"image-{uuid4()}.png"
            file_buffer = BytesIO(base64.b64decode(output.content))
            file_buffer.name = filename
            self.output_files.append(File(name=filename, content=file_buffer.read()))
            return f"Image {filename} got send to the user."

        elif output.type == "error":
            if "ModuleNotFoundError" in output.content:
                if package := re.search(
                    r"ModuleNotFoundError: No module named '(.*)'", output.content
                ):
                    self.codebox.install(package.group(1))
                    return (
                        f"{package.group(1)} was missing but "
                        "got installed now. Please try again."
                    )
            else:
                # TODO: pre-analyze error to optimize next code generation
                pass
            if self.verbose:
                print("Error:", output.content)

        elif modifications := get_file_modifications(code, self.llm):
            for filename in modifications:
                if filename in [file.name for file in self.input_files]:
                    continue
                fileb = self.codebox.download(filename)
                if not fileb.content:
                    continue
                file_buffer = BytesIO(fileb.content)
                file_buffer.name = filename
                self.output_files.append(
                    File(name=filename, content=file_buffer.read())
                )

        return output.content

    async def _arun_handler(self, code: str):
        """Run code in container and send the output to the user"""
        await self.ashow_code(code)
        output: CodeBoxOutput = await self.codebox.arun(code)
        self.code_log.append((code, output.content))

        if not isinstance(output.content, str):
            raise TypeError("Expected output.content to be a string.")

        if output.type == "image/png":
            filename = f"image-{uuid4()}.png"
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
                    return (
                        f"{package.group(1)} was missing but "
                        "got installed now. Please try again."
                    )
            else:
                # TODO: pre-analyze error to optimize next code generation
                pass
            if self.verbose:
                print("Error:", output.content)

        elif modifications := await aget_file_modifications(code, self.llm):
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

    def _input_handler(self, request: UserRequest) -> None:
        """Callback function to handle user input."""
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
            self.codebox.upload(file.name, file.content)
        request.content += "**File(s) are now available in the cwd. **\n"

    async def _ainput_handler(self, request: UserRequest):
        # TODO: variables as context to the agent
        # TODO: current files as context to the agent
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

    def _output_handler(self, final_response: str) -> CodeInterpreterResponse:
        """Embed images in the response"""
        for file in self.output_files:
            if str(file.name) in final_response:
                # rm ![Any](file.name) from the response
                final_response = re.sub(r"\n\n!\[.*\]\(.*\)", "", final_response)

        if self.output_files and re.search(r"\n\[.*\]\(.*\)", final_response):
            try:
                final_response = remove_download_link(final_response, self.llm)
            except Exception as e:
                if self.verbose:
                    print("Error while removing download links:", e)

        output_files = self.output_files
        code_log = self.code_log
        self.output_files = []
        self.code_log = []

        return CodeInterpreterResponse(
            content=final_response, files=output_files, code_log=code_log
        )

    async def _aoutput_handler(self, final_response: str) -> CodeInterpreterResponse:
        """Embed images in the response"""
        for file in self.output_files:
            if str(file.name) in final_response:
                # rm ![Any](file.name) from the response
                final_response = re.sub(r"\n\n!\[.*\]\(.*\)", "", final_response)

        if self.output_files and re.search(r"\n\[.*\]\(.*\)", final_response):
            try:
                final_response = await aremove_download_link(final_response, self.llm)
            except Exception as e:
                if self.verbose:
                    print("Error while removing download links:", e)

        output_files = self.output_files
        code_log = self.code_log
        self.output_files = []
        self.code_log = []

        return CodeInterpreterResponse(
            content=final_response, files=output_files, code_log=code_log
        )

    def generate_response_sync(
        self,
        user_msg: str,
        files: list[File] = [],
        detailed_error: bool = False,
    ) -> CodeInterpreterResponse:
        """Generate a Code Interpreter response based on the user's input."""
        user_request = UserRequest(content=user_msg, files=files)
        try:
            self._input_handler(user_request)
            assert self.agent_executor, "Session not initialized."
            response = self.agent_executor.run(input=user_request.content)
            return self._output_handler(response)
        except Exception as e:
            if self.verbose:
                traceback.print_exc()
            if detailed_error:
                return CodeInterpreterResponse(
                    content="Error in CodeInterpreterSession: "
                    f"{e.__class__.__name__}  - {e}"
                )
            else:
                return CodeInterpreterResponse(
                    content="Sorry, something went while generating your response."
                    "Please try again or restart the session."
                )

    async def generate_response(
        self,
        user_msg: str,
        files: list[File] = [],
        detailed_error: bool = False,
    ) -> CodeInterpreterResponse:
        print(
            "DEPRECATION WARNING: Use agenerate_response for async generation.\n"
            "This function will be converted to sync in the future.\n"
            "You can use generate_response_sync for now.",
        )
        return await self.agenerate_response(
            user_msg=user_msg,
            files=files,
            detailed_error=detailed_error,
        )

    async def agenerate_response(
        self,
        user_msg: str,
        files: list[File] = [],
        detailed_error: bool = False,
    ) -> CodeInterpreterResponse:
        """Generate a Code Interpreter response based on the user's input."""
        user_request = UserRequest(content=user_msg, files=files)
        try:
            await self._ainput_handler(user_request)
            assert self.agent_executor, "Session not initialized."
            response = await self.agent_executor.arun(input=user_request.content)
            return await self._aoutput_handler(response)
        except Exception as e:
            if self.verbose:
                traceback.print_exc()
            if detailed_error:
                return CodeInterpreterResponse(
                    content="Error in CodeInterpreterSession: "
                    f"{e.__class__.__name__}  - {e}"
                )
            else:
                return CodeInterpreterResponse(
                    content="Sorry, something went while generating your response."
                    "Please try again or restart the session."
                )

    def is_running(self) -> bool:
        return self.codebox.status() == "running"

    async def ais_running(self) -> bool:
        return await self.codebox.astatus() == "running"

    def stop(self) -> SessionStatus:
        return SessionStatus.from_codebox_status(self.codebox.stop())

    async def astop(self) -> SessionStatus:
        return SessionStatus.from_codebox_status(await self.codebox.astop())

    def __enter__(self) -> "CodeInterpreterSession":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()

    async def __aenter__(self) -> "CodeInterpreterSession":
        await self.astart()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.astop()
