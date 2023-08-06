import asyncio

from codeinterpreterapi import CodeInterpreterSession


async def run_with_claude():
    async with CodeInterpreterSession(model="claude-2") as session:
        result = await session.generate_response(
            "Plot the nvidea stock vs microsoft stock over the last 6 months."
        )
        result.show()


if __name__ == "__main__":
    asyncio.run(run_with_claude())
