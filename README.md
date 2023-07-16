# Code Interpreter API

A LangChain implementation of the ChatGPT Code Interpreter.
Using CodeBoxes as backend for sandboxed python code execution.
[CodeBox](https://github.com/shroominic/codebox-api/tree/main) is the simplest cloud infrastructure for your LLM Apps.
You can run everything local except the LLM using your own OpenAI API Key.

## Features

- Dataset Analysis, Stock Charting, Image Manipulation, ....
- Internet access and auto Python package installation
- Input `text + files` -> Receive `text + files`
- Conversation Memory: respond based on previous inputs
- Run everything local except the OpenAI API (OpenOrca or others coming soon)
- Use CodeBox API for easy scaling in production (coming soon)

## Installation

Get your OpenAI API Key [here](https://platform.openai.com/account/api-keys) and install the package.

```bash
pip install codeinterpreterapi
```

## Usage

```python
from codeinterpreterapi import CodeInterpreterSession


async def main():
    # start a session
    session = CodeInterpreterSession()
    await session.astart()

    # generate a response based on user input
    output = await session.generate_response(
        "Plot the bitcoin chart of 2023 YTD"
    )
    # show output image in default image viewer
    file = output.files[0]
    file.show_image()

    # show output text
    print("AI: ", output.content)

    # terminate the session
    await session.astop()
    

if __name__ == "__main__":
    import asyncio, os
    os.environ["OPENAI_API_KEY"] = "sk-*********"  # or .env file

    asyncio.run(main())

```

## Output

![Bitcoin YTD](https://github.com/shroominic/codeinterpreter-api/blob/main/examples/assets/bitcoin_chart.png?raw=true)

## Production

In case you want to deploy to production you can use the CodeBox API for easy scaling.

Please contact me if you interested in this, because it's still in early development.

## Contributing

There are some TODOs left in the code
so if you want to contribute feel free to do so.
You can also suggest new features. Code refactoring is also welcome.
Just open an issue or pull request and I will review it.

Also please submit any bugs you find as an issue
with a minimal code example or screenshot.
This helps me a lot to improve the code.

Thanks!

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

You can contact me at [contact@shroominic.com](mailto:contact@shroominic.com).
But I prefer to use [Twitter](https://twitter.com/shroominic) or [Discord](https://gptassistant.app/community) DMs.
