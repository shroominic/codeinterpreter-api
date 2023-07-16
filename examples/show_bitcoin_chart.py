"""
The exciting part about this example is
that the code interpreter has internet access
so it can download the bitcoin chart from yahoo finance
and plot it for you
"""

from datetime import datetime
from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        currentdate = datetime.now().strftime("%Y-%m-%d")

        response = await session.generate_response(
            f"Plot the bitcoin chart of 2023 YTD (today is {currentdate})"
        )

        print("AI: ", response.content)
        for file in response.files:
            file.show_image()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
