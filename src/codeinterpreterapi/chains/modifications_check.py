import json
from typing import List, Optional

from langchain_core.language_models import BaseLanguageModel

from codeinterpreterapi.prompts import determine_modifications_prompt


def get_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 4,
) -> Optional[List[str]]:
    if retry < 1:
        return None

    prompt = determine_modifications_prompt.format(code=code)

    result = llm.invoke(prompt)

    try:
        if isinstance(result.content, str):
            if result.content.endswith("```"):
                result.content = result.content[:-3]
            if result.content.startswith("```"):
                result.content = result.content[3:]
        result = json.loads(result.content)
    except json.JSONDecodeError:
        result = ""
    if not result or not isinstance(result, dict) or "modifications" not in result:
        return get_file_modifications(code, llm, retry=retry - 1)
    return result["modifications"]


async def aget_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 4,
) -> Optional[List[str]]:
    if retry < 1:
        return None

    prompt = determine_modifications_prompt.format(code=code)

    result = await llm.ainvoke(prompt)

    try:
        if isinstance(result.content, str):
            if result.content.endswith("```"):
                result.content = result.content[:-3]
            if result.content.startswith("```"):
                result.content = result.content[3:]
        result = json.loads(result.content)
    except json.JSONDecodeError:
        result = ""
    if not result or not isinstance(result, dict) or "modifications" not in result:
        return await aget_file_modifications(code, llm, retry=retry - 1)
    return result["modifications"]


async def test() -> None:
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI()

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
