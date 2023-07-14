# Code Interpreter API

A LangChain implementation of the ChatGPT Code Interpreter.
Using CodeBoxes as backend for sandboxed python code execution.
[CodeBox](https://github.com/shroominic/codebox-api/tree/main) is the simplest cloud infrastructure for your LLM Apps.
You can run everything local using your own OpenAI API Key.

## Installation

```bash
pip install codeinterpreterapi
```

## Usage

```python
from codeinterpreterapi import CodeInterpreterSession

# start a session
session = CodeInterpreterSession()
await session.astart()

# generate a response based on user input
output = await session.generate_response(
    f"Plot the bitcoin chart of 2023 YTD"
)
# show output image in default image viewer
file = output.files[0]
file.show_image()

# show output text
print("AI: ", output.content)

# terminate the session
await session.stop()

```

## Production

In case you want to deploy to production you can use the CodeBox API for easy scaling.
Please contact me if you want to use the CodeBox API in production.
Its currently in early development and not everything is automated yet.

## Contributing

There are some TODOs left in the code
so if you want to contribute feel free to do so.
You can also suggest new features. Code refactoring is also welcome.
Just open an issue pull request and I will review it.

Also please submit any bugs you find as an issue
with a minimal code example or screenshot.
This helps me a lot to improve the code.

Thanks!

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contact

You can contact me at [pleurae-berets.0u@icloud.com](mailto:pleurae-berets.0u@icloud.com)
Sorry for the weird email address but I don't want to get spammed so I can deactivate it if necessary.
But you can also contact me on [Twitter](https://twitter.com/shroominic) or [Discord](https://gptassistant.app/community).
