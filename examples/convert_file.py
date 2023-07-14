from codeinterpreterapi import CodeInterpreterSession
from codeinterpreterapi.schema import File


async def main():
    async with CodeInterpreterSession() as session:
        user_request = "Convert this dataset to excel."
        files = [
            File.from_path("examples/assets/iris.csv"),
        ]

        output = await session.generate_response(user_request, files=files)
        file = output.files[0]

        file.save("examples/assets/Iris.xlsx")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
