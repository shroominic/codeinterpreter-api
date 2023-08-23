import asyncio

from langchain.pydantic_v1 import BaseModel


class File(BaseModel):
    name: str
    content: bytes

    @classmethod
    def from_path(cls, path: str):
        if not path.startswith("/"):
            path = f"./{path}"
        with open(path, "rb") as f:
            path = path.split("/")[-1]
            return cls(name=path, content=f.read())

    @classmethod
    async def afrom_path(cls, path: str):
        return await asyncio.to_thread(cls.from_path, path)

    @classmethod
    def from_url(cls, url: str):
        import requests  # type: ignore

        r = requests.get(url)
        return cls(name=url.split("/")[-1], content=r.content)

    @classmethod
    async def afrom_url(cls, url: str):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                return cls(name=url.split("/")[-1], content=await r.read())

    def save(self, path: str):
        if not path.startswith("/"):
            path = f"./{path}"
        with open(path, "wb") as f:
            f.write(self.content)

    async def asave(self, path: str):
        await asyncio.to_thread(self.save, path)

    def get_image(self):
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            print(
                "Please install it with "
                "`pip install 'codeinterpreterapi[image_support]'`"
                " to display images."
            )
            exit(1)

        from io import BytesIO

        img_io = BytesIO(self.content)
        img = Image.open(img_io)

        # Convert image to RGB if it's not
        if img.mode not in ("RGB", "L"):  # L is for grayscale images
            img = img.convert("RGB")

        return img

    def show_image(self):
        img = self.get_image()
        # Display the image
        try:
            # Try to get the IPython shell if available.
            shell = get_ipython().__class__.__name__  # type: ignore
            # If the shell is in a Jupyter notebook or similar.
            if shell == "ZMQInteractiveShell" or shell == "Shell":
                from IPython.display import display  # type: ignore

                display(img)
            else:
                img.show()
        except NameError:
            img.show()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"File(name={self.name})"
