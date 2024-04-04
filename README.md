# 👾 Code Interpreter API

[![Version](https://badge.fury.io/py/codeinterpreterapi.svg)](https://badge.fury.io/py/codeinterpreterapi)
![Downloads](https://img.shields.io/pypi/dm/codeinterpreterapi)
![License](https://img.shields.io/pypi/l/codeinterpreterapi)
![PyVersion](https://img.shields.io/pypi/pyversions/codeinterpreterapi)

A [LangChain](https://github.com/langchain-ai/langchain) implementation of the ChatGPT Code Interpreter.
Using CodeBoxes as backend for sandboxed python code execution.
[CodeBox](https://github.com/shroominic/codebox-api/tree/main) is the simplest cloud infrastructure for your LLM Apps.
You can run everything local except the LLM using your own OpenAI API Key.

## Features

- Dataset Analysis, Stock Charting, Image Manipulation, ....
- Internet access and auto Python package installation
- Input `text + files` -> Receive `text + files`
- Conversation Memory: respond based on previous inputs
- Run everything local except the OpenAI API (OpenOrca or others maybe soon)
- Use CodeBox API for easy scaling in production

## Docs

Checkout the [documentation](https://shroominic.github.io/codeinterpreter-api/) for more information.

## Installation

Get your OpenAI API Key [here](https://platform.openai.com/account/api-keys) and install the package.

```bash
pip install "codeinterpreterapi[all]"
```

Everything for local experiments are installed with the `all` extra.
For deployments, you can use `pip install codeinterpreterapi` instead which does not install the additional dependencies.

## Usage

To configure OpenAI and Azure OpenAI, ensure that you set the appropriate environment variables (or use a .env file):

For OpenAI, set the OPENAI_API_KEY environment variable:

```bash
export OPENAI_API_KEY=sk-**********
```

```python
from codeinterpreterapi import CodeInterpreterSession, settings


# create a session and close it automatically
with CodeInterpreterSession() as session:
    # generate a response based on user input
    response = session.generate_response(
        "Plot the bitcoin chart of year 2023"
    )
    # output the response
    response.show()
```

![Bitcoin YTD](https://github.com/shroominic/codeinterpreter-api/blob/main/examples/assets/bitcoin_chart.png?raw=true)
Bitcoin YTD Chart Output

## Dataset Analysis

```python
from codeinterpreterapi import CodeInterpreterSession, File

# this example uses async but normal sync like above works too
async def main():
    # context manager for auto start/stop of the session
    async with CodeInterpreterSession() as session:
        # define the user request
        user_request = "Analyze this dataset and plot something interesting about it."
        files = [
            # attach files to the request
            File.from_path("examples/assets/iris.csv"),
        ]

        # generate the response
        response = await session.generate_response(
            user_request, files=files
        )

        # output to the user
        print("AI: ", response.content)
        for file in response.files:
            # iterate over the files (display if image)
            file.show_image()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

![Iris Dataset Analysis](https://github.com/shroominic/codeinterpreter-api/blob/main/examples/assets/iris_analysis.png?raw=true)
Iris Dataset Analysis Output

## Production

In case you want to deploy to production, you can utilize the CodeBox API for seamless scalability.

Please contact me if you are interested in this, as it is still in the early stages of development.

## Contributing

There are some remaining TODOs in the code.
So, if you want to contribute, feel free to do so.
You can also suggest new features. Code refactoring is also welcome.
Just open an issue or pull request and I will review it.

Please also submit any bugs you find as an issue with a minimal code example or screenshot.
This helps me a lot in improving the code.

## Contact

You can contact me at [contact@shroominic.com](mailto:contact@shroominic.com).
But I prefer to use [Twitter](https://twitter.com/shroominic) or [Discord](https://discord.gg/Vaq25XJvvW) DMs.

## Support this project

If you would like to help this project with a donation, you can [click here](https://ko-fi.com/shroominic).
Thanks, this helps a lot! ❤️
