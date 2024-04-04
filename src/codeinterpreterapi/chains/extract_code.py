from langchain_core.language_models import BaseLanguageModel


def extract_python_code(
    text: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> str:
    return "TODO"


async def aextract_python_code(
    text: str,
    llm: BaseLanguageModel,
    retry: int = 2,
) -> str:
    return "TODO"


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

    print(extract_python_code(code, llm))


if __name__ == "__main__":
    import asyncio

    import dotenv

    dotenv.load_dotenv()

    asyncio.run(test())
