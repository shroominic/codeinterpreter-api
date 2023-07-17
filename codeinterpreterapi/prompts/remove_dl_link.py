from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    SystemMessage,
    HumanMessage,
)


remove_dl_link_prompt = ChatPromptTemplate(
    input_variables=["input_response"],
    messages=[
        SystemMessage(
            content="The user will send you a response and you need to remove the download link from it.\n"
            "Reformat the remaining message so no whitespace or half sentences are still there.\n"
            "If the response does not contain a download link, return the response as is.\n"
        ),
        HumanMessage(
            content="The dataset has been successfully converted to CSV format. You can download the converted file [here](sandbox:/Iris.csv)."
        ),
        AIMessage(content="The dataset has been successfully converted to CSV format."),
        HumanMessagePromptTemplate.from_template("{input_response}"),
    ],
)