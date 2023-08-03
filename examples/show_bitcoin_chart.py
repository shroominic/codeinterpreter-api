from datetime import datetime

from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        currentdate = datetime.now().strftime("%Y-%m-%d")

        response = await session.generate_response(
            f"Plot the bitcoin chart of 2023 YTD (today is {currentdate})"
        )

        # prints the text and shows the image
        response.show()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
