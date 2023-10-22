# UserRequest

The UserRequest class represents the user input to the agent.

It contains:

- `content`: text content of user message
- `files`: list of File attachments

Usage:

```python
from codeinterpreterapi import UserRequest, File

request = UserRequest(
  content="Here is an image",
  files=[File.from_path("image.png")]
)
```
