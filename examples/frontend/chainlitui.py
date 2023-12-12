import chainlit as cl  # type: ignore
from codeinterpreterapi import CodeInterpreterSession
from codeinterpreterapi import File as CIFile

UPLOADED_FILES: list[CIFile] = []


@cl.action_callback("upload_file")
async def on_action(action: cl.Action) -> None:
    files = None

    # Wait for the user to upload a file
    while files is None:
        files = await cl.AskFileMessage(
            content="Please upload a text file to begin!", accept=["text/csv"]
        ).send()
    # Decode the file
    text_file = files[0]
    text = text_file.content.decode("utf-8")

    UPLOADED_FILES.append(text_file)

    # Let the user know that the system is ready
    await cl.Message(
        content=f"`{text_file.name}` uploaded, it contains {len(text)} characters!"
    ).send()
    await action.remove()


@cl.on_chat_start
async def start_chat() -> None:
    actions = [
        cl.Action(name="upload_file", value="example_value", description="Upload file")
    ]

    await cl.Message(
        content="Hello, How can I assist you today", actions=actions
    ).send()


@cl.on_message
async def run_conversation(user_message: str) -> None:
    session = CodeInterpreterSession()
    await session.astart()

    files = [CIFile(name=it.name, content=it.content) for it in UPLOADED_FILES]

    response = await session.agenerate_response(user_message, files=files)
    elements = [
        cl.Image(
            content=file.content,
            name=f"code-interpreter-image-{file.name}",
            display="inline",
        )
        for file in response.files
    ]
    actions = [
        cl.Action(name="upload_file", value="example_value", description="Upload file")
    ]
    await cl.Message(
        content=response.content,
        elements=elements,
        actions=actions,
    ).send()

    await session.astop()
