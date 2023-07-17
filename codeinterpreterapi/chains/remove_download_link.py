from langchain.base_language import BaseLanguageModel
from langchain.chat_models.openai import ChatOpenAI
from langchain.schema import AIMessage, OutputParserException

from codeinterpreterapi.prompts import remove_dl_link_prompt


async def remove_download_link(
    input_response: str,
    llm: BaseLanguageModel,
) -> str:
    messages = remove_dl_link_prompt.format_prompt(input_response=input_response).to_messages()
    message = await llm.apredict_messages(messages)

    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")

    return message.content


async def test():
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613")  # type: ignore

    example = "I have created the plot to your dataset.\n\nLink to the file [here](sandbox:/plot.png)."

    print(await remove_download_link(example, llm))


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(test())
