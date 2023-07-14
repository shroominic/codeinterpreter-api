from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        user_request = "Plot a sin wave and show it to me."
        output = await session.generate_response(user_request)
        
        print(output.content)
        print(output.files)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
