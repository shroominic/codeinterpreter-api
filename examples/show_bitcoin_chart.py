from datetime import datetime
from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        currentdate = datetime.now().strftime("%Y-%m-%d")
        user_request = f"Plot the bitcoin chart of 2023 YTD (today is {currentdate})"
        
        output = await session.generate_response(user_request)
        
        file = output.files[0]
        file.show_image()


# The exciting part about this example is
# that the code interpreter has internet access
# so it can download the bitcoin chart from yahoo finance
# and plot it for you


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
