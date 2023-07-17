
from langchain.schema import SystemMessage
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate


determine_modifications_prompt = ChatPromptTemplate(
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


determine_modifications_function = {
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
