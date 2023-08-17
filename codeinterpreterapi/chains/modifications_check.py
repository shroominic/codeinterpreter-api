import json
from typing import List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chat_models.anthropic import ChatAnthropic

from codeinterpreterapi.prompts import determine_modifications_prompt


def get_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> Optional[List[str]]:
    if retry < 1:
        return None

    prompt = determine_modifications_prompt.format(code=code)

    result = llm.predict(prompt, stop="```")

    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        result = ""
    if not result or not isinstance(result, dict) or "modifications" not in result:
        return get_file_modifications(code, llm, retry=retry - 1)
    return result["modifications"]


async def aget_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> Optional[List[str]]:
    if retry < 1:
        return None

    prompt = determine_modifications_prompt.format(code=code)

    result = await llm.apredict(prompt, stop="```")

    try:
        result = json.loads(result)
    except json.JSONDecodeError:
        result = ""
    if not result or not isinstance(result, dict) or "modifications" not in result:
        return await aget_file_modifications(code, llm, retry=retry - 1)
    return result["modifications"]


async def test():
    llm = ChatAnthropic(model="claude-2")  # type: ignore

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

    print(get_file_modifications(code, llm))


if __name__ == "__main__":
    import asyncio

    import dotenv

    dotenv.load_dotenv()

    asyncio.run(test())
