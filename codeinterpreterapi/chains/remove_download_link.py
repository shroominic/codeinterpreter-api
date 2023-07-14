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
    HumanMessage
)


prompt = ChatPromptTemplate(
    input_variables=["input_response"],
    messages=[
        SystemMessage(content=
            "The user will send you a response and you need to remove the download link from it.\n"
            "Reformat the remaining message so no whitespace or half sentences are still there.\n"
            "If the response does not contain a download link, return the response as is.\n"
        ),
        HumanMessage(content="The dataset has been successfully converted to CSV format. You can download the converted file [here](sandbox:/Iris.csv)."),
        AIMessage(content="The dataset has been successfully converted to CSV format."),
        HumanMessagePromptTemplate.from_template("{input_response}")
    ]
)


async def remove_download_link(
    input_response: str, 
    llm: BaseLanguageModel,
) -> str:
    messages = prompt.format_prompt(input_response=input_response).to_messages()
    message = await llm.apredict_messages(messages)
    
    if not isinstance(message, AIMessage):
        raise OutputParserException("Expected an AIMessage")
    
    return message.content
    

async def test():
    llm = ChatOpenAI(model="gpt-3.5-turbo-0613")  # type: ignore
    
    example = "I have created the plot to your dataset.\n\nLink to the file [here](sandbox:/plot.png)."
    
    modifications = await remove_download_link(example, llm)
    
    print(modifications)


if __name__ == "__main__":
    import asyncio
    import dotenv
    dotenv.load_dotenv()
    
    asyncio.run(test())
