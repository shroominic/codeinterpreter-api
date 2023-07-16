from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        response = await session.generate_response(
            "Plot a sin wave and show it to me."
        )

        print("AI: ", response.content)
        for file in response.files:
            file.show_image()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
