import json
from typing import List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.chat_models.anthropic import ChatAnthropic
from langchain.schema import AIMessage, OutputParserException

# from codeinterpreterapi.prompts import extract_code_prompt


async def extract_python_code(
    text: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> Optional[str]:
    pass
    

async def test():
    llm = ChatAnthropic(model="claude-1.3")  # type: ignore
    
    code = \
        """
        import matplotlib.pyplot as plt

        x = list(range(1, 11))
        y = [29, 39, 23, 32, 4, 43, 43, 23, 43, 77]

        plt.plot(x, y, marker='o')
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Data Plot')

        plt.show()
        """
    
    print(await extract_python_code(code, llm))
    

if __name__ == "__main__":
    import asyncio, dotenv
    dotenv.load_dotenv()

    asyncio.run(test())
