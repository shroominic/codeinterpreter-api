# Deployment
CodeInterpreterAPI can be easily deployed to production using the CodeBox framework.

## Prerequisites
- CodeBox API key
  - Get your API key from [CodeBox](https://pay.codeboxapi.com/b/00g3e6dZX2fTg0gaEE) (get 70% with the code `BETA`)
- CodeInterpreterAPI installed
  - `pip install codeinterpreterapi`

## Setup

Set the `CODEBOX_API_KEY` environment variable or directly in your code:

```python
from codeinterpreterapi import settings

settings.CODEBOX_API_KEY = "sk-..."
```

## Starting a Session

To start a code interpreter session using CodeBox:

```python
from uuid import uuid4
from codeinterpreterapi import CodeInterpreterSession

session_id = uuid4()

session = CodeInterpreterSession.from_id(session_id)
session.start()
```

The `session_id` allows restoring the session later after restarting the application.

## Generating Responses

With the session started, you can now generate responses like normal:

```python
response = session.generate_response(
  "Plot a histogram of the iris dataset"
)

response.show()
```

This will execute the code securely using CodeBox.

## Stopping the Session

Don't forget to stop the session when finished:

```python
session.stop()
```

This will shutdown the CodeBox instance.

## Next Steps

- See the [CodeBox docs](https://codeboxapi.com/docs) for more details on deployment options.
- Look at the [examples](https://github.com/shroominic/codebox-api/tree/main/examples) for more usage ideas.
- Contact [Shroominic](https://twitter.com/shroominic) for assistance with scaling.
