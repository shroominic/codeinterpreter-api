import json
from json import JSONDecodeError
from typing import List

from langchain.base_language import BaseLanguageModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    OutputParserException,
    SystemMessage,
)


prompt = ChatPromptTemplate(
    input_variables=["code"],
    messages=[
        SystemMessage(
            content="The user will input some code and you will need to determine if the code makes any changes to the file system. \n"
            "With changes it means creating new files or modifying exsisting ones.\n"
            "Answer with a function call `determine_modifications` and list them inside.\n"
            "If the code does not make any changes to the file system, still answer with the function call but return an empty list.\n",
        ),
        HumanMessagePromptTemplate.from_template("{code}"),
    ],
)

functions = [
    {
        "name": "determine_modifications",
        "description": "Based on code of the user determine if the code makes any changes to the file system. \n"
        "With changes it means creating new files or modifying exsisting ones.\n",
        "parameters": {
            "type": "object",
            "properties": {
                "modifications": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The filenames that are modified by the code.",
                },
            },
            "required": ["modifications"],
        },
    }
]


async def get_file_modifications(
    code: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> List[str] | None:
    if retry < 1:
        return None
    messages = prompt.format_prompt(code=code).to_messages()
    message = await llm.apredict_messages(messages, functions=functions)

    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")

    function_call = message.additional_kwargs.get("function_call", None)

    if function_call is None:
        return await get_file_modifications(code, llm, retry=retry - 1)
    else:
        function_call = json.loads(function_call["arguments"])
        return function_call["modifications"]


async def test():
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613")  # type: ignore

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

    code2 = "import pandas as pd\n\n# Read the Excel file\ndata = pd.read_excel('Iris.xlsx')\n\n# Convert the data to CSV\ndata.to_csv('Iris.csv', index=False)"

    modifications = await get_file_modifications(code2, llm)

    print(modifications)


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    asyncio.run(test())
