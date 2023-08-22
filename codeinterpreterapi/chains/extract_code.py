from langchain.base_language import BaseLanguageModel
from langchain.chat_models.anthropic import ChatAnthropic


def extract_python_code(
    text: str,
    llm: BaseLanguageModel,
    retry: int = 2,
):
    pass  # TODO


async def aextract_python_code(
    text: str,
    llm: BaseLanguageModel,
    retry: int = 2,
):
    pass  # TODO


async def test():
    llm = ChatAnthropic(model="claude-1.3")  # type: ignore

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

    print(extract_python_code(code, llm))


if __name__ == "__main__":
    import asyncio

    import dotenv

    dotenv.load_dotenv()

    asyncio.run(test())
