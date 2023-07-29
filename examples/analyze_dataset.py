from codeinterpreterapi import CodeInterpreterSession, File
from langchain.chat_models.anthropic import ChatAnthropic


async def main():
    llm = ChatAnthropic(model="claude-2")
    # context manager for start/stop of the session
    async with CodeInterpreterSession(llm=llm) as session:
        # define the user request
        user_request = "Analyze this dataset and plot something interesting about it."
        files = [
            File.from_path("examples/assets/iris.csv"),
        ]
        
        # generate the response
        response = await session.generate_response(
            user_request, files=files
        )

        # output the response (text + image)
        print("AI: ", response.content)
        for file in response.files:
            file.show_image()


if __name__ == "__main__":
    import asyncio

    # run the async function
    asyncio.run(main())
