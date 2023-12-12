# Usage

To create a session and generate a response:

```python
from codeinterpreterapi import CodeInterpreterSession, settings

# set api key (or automatically loads from env vars)
settings.OPENAI_API_KEY = "sk-***************"

# create a session
with CodeInterpreterSession() as session:
    # generate a response based on user input
    response = session.generate_response(
        "Plot the bitcoin chart of year 2023"
    )

    # output the response
    response.show()
```
