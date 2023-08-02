from __future__ import annotations
import re
from typing import Union

from langchain.agents import AgentOutputParser
from langchain.output_parsers.json import parse_json_markdown
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.chat_models.base import BaseChatModel
from codeinterpreterapi.chains import extract_python_code


class CodeAgentOutputParser(AgentOutputParser):
    ai_prefix: str = "AI"

    def get_format_instructions(self) -> str:
        from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if f"{self.ai_prefix}:" in text:
            return AgentFinish(
                {"output": text.split(f"{self.ai_prefix}:")[-1].strip()}, text
            )
        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{text}`")
        action = match.group(1)
        action_input = match.group(2)
        return AgentAction(action.strip(), action_input.strip(" ").strip('"'), text)

    @property
    def _type(self) -> str:
        return "conversational"
    
    
class CodeChatAgentOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        from langchain.agents.conversational_chat.prompt import FORMAT_INSTRUCTIONS
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str, llm: BaseChatModel) -> Union[AgentAction, AgentFinish]:
        try:
            response = parse_json_markdown(text)
            action, action_input = response["action"], response["action_input"]
            if action == "Final Answer":
                return AgentFinish({"output": action_input}, text)
            else:
                return AgentAction(action, action_input, text)
        except Exception as e:
            if '"action": "python"' in text:
                # extract python code from text with prompt
                text = extract_python_code(text, llm=llm)
                match = re.search(r"```python\n(.*?)```", text)
                if match:
                    code = match.group(1).replace("\\n", "; ")
                    return AgentAction("python", code, text)

            raise OutputParserException(f"Could not parse LLM output: `{text}`")
                

    @property
    def _type(self) -> str:
        return "conversational_chat"