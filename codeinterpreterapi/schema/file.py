import asyncio
from pydantic import BaseModel


class File(BaseModel):
    name: str
    content: bytes

    @classmethod
    def from_path(cls, path: str):
        with open(path, "rb") as f:
            path = path.split("/")[-1]
            return cls(name=path, content=f.read())

    @classmethod
    async def afrom_path(cls, path: str):
        await asyncio.to_thread(cls.from_path, path)

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
        with open(path, "wb") as f:
            f.write(self.content)

    async def asave(self, path: str):
        await asyncio.to_thread(self.save, path)

    def show_image(self):
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            print(
                "Please install it with `pip install codeinterpreterapi[image_support]` to display images."
            )
            exit(1)

        from io import BytesIO

        img_io = BytesIO(self.content)
        img = Image.open(img_io)

        # Display the image
        img.show()

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"File(name={self.name})"
