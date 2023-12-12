# File Object

The File class is used to represent files that are uploaded or downloaded during the session.

It stores the filename and binary content of the file.

It provides utility methods like:

- `from_path()`: Create File from filesystem path
- `from_url` - Create File from URL
- `save()`: Save File to filesystem path
- `show_image()`: Display image File

Usage:

```python
from codeinterpreterapi import File

file = File.from_path("image.png")
file.show_image() # display image
file.save("copy.png") # save copy
```

File objects can be passed to `CodeInterpreterSession.generate_response` to make them available to the agent.
