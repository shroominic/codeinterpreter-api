from codeinterpreterapi import CodeInterpreterSession, File


async def main() -> None:
    # context manager for start/stop of the session
    async with CodeInterpreterSession() as session:
        # define the user request
        user_request = "Analyze this dataset and plot something interesting about it."
        files = [
            File.from_path("examples/assets/iris.csv"),
        ]

        # generate the response
        response = await session.agenerate_response(user_request, files=files)

        # output the response (text + image)
        response.show()


if __name__ == "__main__":
    import asyncio

    # run the async function
    asyncio.run(main())
