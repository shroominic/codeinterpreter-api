from codeinterpreterapi import CodeInterpreterSession


async def main():
    async with CodeInterpreterSession() as session:
        user_request = "Plot a sin wave and show it to me."
        output = await session.generate_response(user_request)
        
        print(output.content)

        try:
            from PIL import Image  # type: ignore
        except ImportError:
            print("Please install it with `pip install codeinterpreterapi[image_support]` to display images.")
            exit(1)

        from io import BytesIO
        file = output.files[0]
        img_io = BytesIO(file.content)
        img = Image.open(img_io)
        
        # Display the image
        img.show()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
