import base64
import re
import traceback
from io import BytesIO
from types import TracebackType
from typing import Any, Optional, Type
from uuid import UUID, uuid4

from codeboxapi import CodeBox  # type: ignore
from codeboxapi.schema import CodeBoxOutput  # type: ignore
from langchain.agents import (
    AgentExecutor,
    BaseSingleActionAgent,
    ConversationalAgent,
    ConversationalChatAgent,
)
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.callbacks.base import Callbacks
from langchain.chat_models.base import BaseChatModel
from langchain.memory.buffer import ConversationBufferMemory
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.chat_message_histories.postgres import (
    PostgresChatMessageHistory,
)
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.tools import BaseTool, StructuredTool
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from codeinterpreterapi.chains import (
    aget_file_modifications,
    aremove_download_link,
    get_file_modifications,
    remove_download_link,
)
from codeinterpreterapi.chat_history import CodeBoxChatMessageHistory
from codeinterpreterapi.config import settings
from codeinterpreterapi.schema import (
    CodeInput,
    CodeInterpreterResponse,
    File,
    SessionStatus,
    UserRequest,
)


def _handle_deprecated_kwargs(kwargs: dict) -> None:
    settings.MODEL = kwargs.get("model", settings.MODEL)
    settings.MAX_RETRY = kwargs.get("max_retry", settings.MAX_RETRY)
    settings.TEMPERATURE = kwargs.get("temperature", settings.TEMPERATURE)
    settings.OPENAI_API_KEY = kwargs.get("openai_api_key", settings.OPENAI_API_KEY)
    settings.SYSTEM_MESSAGE = kwargs.get("system_message", settings.SYSTEM_MESSAGE)
    settings.MAX_ITERATIONS = kwargs.get("max_iterations", settings.MAX_ITERATIONS)


class CodeInterpreterSession:
    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        additional_tools: list[BaseTool] = [],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> None:
        _handle_deprecated_kwargs(kwargs)
        self.codebox = CodeBox(requirements=settings.CUSTOM_PACKAGES)
        self.verbose = kwargs.get("verbose", settings.DEBUG)
        self.tools: list[BaseTool] = self._tools(additional_tools)
        self.llm: BaseLanguageModel = llm or self._choose_llm()
        self.callbacks = callbacks
        self.agent_executor: Optional[AgentExecutor] = None
        self.input_files: list[File] = []
        self.output_files: list[File] = []
        self.code_log: list[tuple[str, str]] = []

    @classmethod
    def from_id(cls, session_id: UUID, **kwargs: Any) -> "CodeInterpreterSession":
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
        self.codebox.run(
            f"!pip install -q {' '.join(settings.CUSTOM_PACKAGES)}",
        )
        return status

    async def astart(self) -> SessionStatus:
        status = SessionStatus.from_codebox_status(await self.codebox.astart())
        self.agent_executor = self._agent_executor()
        await self.codebox.arun(
            f"!pip install -q {' '.join(settings.CUSTOM_PACKAGES)}",
        )
        return status

    def _tools(self, additional_tools: list[BaseTool]) -> list[BaseTool]:
        return additional_tools + [
            StructuredTool(
                name="python",
                description="Input a string of code to a ipython interpreter. "
                "Write the entire code in a single string. This string can "
                "be really long, so you can use the `;` character to split lines. "
                "Start your code on the same line as the opening quote. "
                "Do not start your code with a line break. "
                "For example, do 'import numpy', not '\\nimport numpy'."
                "Variables are preserved between runs. "
                + (
                    (
                        "You can use all default python packages "
                        f"specifically also these: {settings.CUSTOM_PACKAGES}"
                    )
                    if settings.CUSTOM_PACKAGES
                    else ""
                ),  # TODO: or include this in the system message
                func=self._run_handler,
                coroutine=self._arun_handler,
                args_schema=CodeInput,  # type: ignore
            ),
        ]

    def _choose_llm(self) -> BaseChatModel:
        if (
            settings.AZURE_OPENAI_API_KEY
            and settings.AZURE_API_BASE
            and settings.AZURE_API_VERSION
            and settings.AZURE_DEPLOYMENT_NAME
        ):
            self.log("Using Azure Chat OpenAI")
            return AzureChatOpenAI(
                temperature=0.03,
                base_url=settings.AZURE_API_BASE,
                api_version=settings.AZURE_API_VERSION,
                azure_deployment=settings.AZURE_DEPLOYMENT_NAME,
                api_key=settings.AZURE_OPENAI_API_KEY,  # type: ignore
                max_retries=settings.MAX_RETRY,
                timeout=settings.REQUEST_TIMEOUT,
            )  # type: ignore
        if settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=settings.MODEL,
                api_key=settings.OPENAI_API_KEY,  # type: ignore
                timeout=settings.REQUEST_TIMEOUT,
                temperature=settings.TEMPERATURE,
                max_retries=settings.MAX_RETRY,
            )  # type: ignore
        if settings.ANTHROPIC_API_KEY:
            from langchain_anthropic import ChatAnthropic  # type: ignore

            if "claude" not in settings.MODEL:
                print("Please set the claude model in the settings.")
            self.log("Using Chat Anthropic")
            return ChatAnthropic(
                model_name=settings.MODEL,
                temperature=settings.TEMPERATURE,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
            )
        raise ValueError("Please set the API key for the LLM you want to use.")

    def _choose_agent(self) -> BaseSingleActionAgent:
        return (
            OpenAIFunctionsAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                system_message=settings.SYSTEM_MESSAGE,
                extra_prompt_messages=[
                    MessagesPlaceholder(variable_name="chat_history")
                ],
            )
            if isinstance(self.llm, ChatOpenAI) or isinstance(self.llm, AzureChatOpenAI)
            else ConversationalChatAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                system_message=settings.SYSTEM_MESSAGE.content.__str__(),
            )
            if isinstance(self.llm, BaseChatModel)
            else ConversationalAgent.from_llm_and_tools(
                llm=self.llm,
                tools=self.tools,
                prefix=settings.SYSTEM_MESSAGE.content.__str__(),
            )
        )

    def _history_backend(self) -> BaseChatMessageHistory:
        return (
            CodeBoxChatMessageHistory(codebox=self.codebox)  # type: ignore
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
            max_iterations=settings.MAX_ITERATIONS,
            tools=self.tools,
            verbose=self.verbose,
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                chat_memory=self._history_backend(),
            ),
            callbacks=self.callbacks,
        )

    def show_code(self, code: str) -> None:
        if self.verbose:
            print(code)

    async def ashow_code(self, code: str) -> None:
        """Callback function to show code to the user."""
        if self.verbose:
            print(code)

    def _run_handler(self, code: str) -> str:
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
                    r"ModuleNotFoundError: No module named '(.*)'",
                    output.content,
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

        elif modifications := get_file_modifications(code, self.llm):  # type: ignore
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

    async def _arun_handler(self, code: str) -> str:
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
                    r"ModuleNotFoundError: No module named '(.*)'",
                    output.content,
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
        assert isinstance(request.content, str), "TODO: implement image support"
        request.content += "\n**The user uploaded the following files: **\n"
        for file in request.files:
            self.input_files.append(file)
            request.content += f"[Attachment: {file.name}]\n"
            self.codebox.upload(file.name, file.content)
        request.content += "**File(s) are now available in the cwd. **\n"

    async def _ainput_handler(self, request: UserRequest) -> None:
        # TODO: variables as context to the agent
        # TODO: current files as context to the agent
        if not request.files:
            return
        if not request.content:
            request.content = (
                "I uploaded, just text me back and confirm that you got the file(s)."
            )
        assert isinstance(request.content, str), "TODO: implement image support"
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
    ) -> CodeInterpreterResponse:
        print("DEPRECATION WARNING: Use generate_response for sync generation.\n")
        return self.generate_response(
            user_msg=user_msg,
            files=files,
        )

    def generate_response(
        self,
        user_msg: str,
        files: list[File] = [],
    ) -> CodeInterpreterResponse:
        """Generate a Code Interpreter response based on the user's input."""
        user_request = UserRequest(content=user_msg, files=files)
        try:
            self._input_handler(user_request)
            assert self.agent_executor, "Session not initialized."
            response = self.agent_executor.invoke({"input": user_request.content})
            return self._output_handler(response["output"])
        except Exception as e:
            if self.verbose:
                traceback.print_exc()
            if settings.DETAILED_ERROR:
                return CodeInterpreterResponse(
                    content="Error in CodeInterpreterSession: "
                    f"{e.__class__.__name__}  - {e}"
                )
            else:
                return CodeInterpreterResponse(
                    content="Sorry, something went while generating your response."
                    "Please try again or restart the session."
                )

    async def agenerate_response(
        self,
        user_msg: str,
        files: list[File] = [],
    ) -> CodeInterpreterResponse:
        """Generate a Code Interpreter response based on the user's input."""
        user_request = UserRequest(content=user_msg, files=files)
        try:
            await self._ainput_handler(user_request)
            assert self.agent_executor, "Session not initialized."
            response = await self.agent_executor.ainvoke(
                {"input": user_request.content}
            )
            return await self._aoutput_handler(response["output"])
        except Exception as e:
            if self.verbose:
                traceback.print_exc()
            if settings.DETAILED_ERROR:
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

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

    def stop(self) -> SessionStatus:
        return SessionStatus.from_codebox_status(self.codebox.stop())

    async def astop(self) -> SessionStatus:
        return SessionStatus.from_codebox_status(await self.codebox.astop())

    def __enter__(self) -> "CodeInterpreterSession":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.stop()

    async def __aenter__(self) -> "CodeInterpreterSession":
        await self.astart()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.astop()
