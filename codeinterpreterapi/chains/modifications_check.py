import json
from typing import List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema import AIMessage, OutputParserException

from codeinterpreterapi.prompts import determine_modifications_function, determine_modifications_prompt


async def get_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> Optional[List[str]]:
    if retry < 1:
        return None
    messages = determine_modifications_prompt.format_prompt(code=code).to_messages()
    message = await llm.apredict_messages(messages, functions=[determine_modifications_function])

    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")

    function_call = message.additional_kwargs.get("function_call", None)

    if function_call is None:
        return await get_file_modifications(code, llm, retry=retry - 1)
    else:
        function_call = json.loads(function_call["arguments"])
        return function_call["modifications"]


async def test():
    llm = ChatOpenAI(model="gpt-3.5")  # type: ignore

    code = """
    import matplotlib.pyplot as plt

    x = list(range(1, 11))
    y = [29, 39, 23, 32, 4, 43, 43, 23, 43, 77]

    plt.plot(x, y, marker='o')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Data Plot')

    plt.show()
    """

    print(await get_file_modifications(code, llm))


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(test())
