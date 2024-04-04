from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from codeinterpreterapi.prompts import remove_dl_link_prompt


def remove_download_link(
    input_response: str,
    llm: BaseLanguageModel,
) -> str:
    messages = remove_dl_link_prompt.format_prompt(
        input_response=input_response
    ).to_messages()
    message = llm.invoke(messages)

    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")

    assert isinstance(message.content, str), "TODO: add image support"
    return message.content


async def aremove_download_link(
    input_response: str,
    llm: BaseLanguageModel,
) -> str:
    messages = remove_dl_link_prompt.format_prompt(
        input_response=input_response
    ).to_messages()
    message = await llm.ainvoke(messages)

    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")

    assert isinstance(message.content, str), "TODO: add image support"
    return message.content


def test() -> None:
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613")  # type: ignore

    example = (
        "I have created the plot to your dataset.\n\n"
        "Link to the file [here](sandbox:/plot.png)."
    )
    print(remove_download_link(example, llm))


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    test()
