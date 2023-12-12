from codeinterpreterapi import CodeInterpreterSession


async def main() -> None:
    async with CodeInterpreterSession() as session:
        response = await session.agenerate_response(
            "Plot a sin wave and show it to me."
        )
        response.show()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
