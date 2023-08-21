# TODO: implement test that runs all examples and checks that they don't crash
import sys, os
sys.path.insert(
    0, os.path.abspath("../")
)  # Adds the parent directory to the system path
import codeinterpreterapi

from codeinterpreterapi import CodeInterpreterSession

async def main():
    # create a session
    session = CodeInterpreterSession(verbose=True, model="replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781", debugger=True, email="test@berri.ai")
    await session.astart()

    # generate a response based on user input
    response = await session.generate_response(
        "Plot the bitcoin chart of 2023 YTD"
    )

    # output the response (text + image)
    print("AI: ", response.content)
    for file in response.files:
        file.show_image()

    # terminate the session
    await session.astop()


if __name__ == "__main__":
    import asyncio
    # run the async function
    asyncio.run(main())
