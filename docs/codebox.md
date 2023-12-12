# CodeBox

The CodeBox class provides the isolated secure environment for executing python code. It is used by the CodeInterpreterSession internally.

It provides methods like:

- `upload() / download()`: Upload and download files
- `run()`: Run python code
- `install()`: Install python packages

The CodeBox handles setting up the environment, installing packages, running code, capturing output and making it available.

It uses Docker containers under the hood to provide the isolated env.

Usage:

```python
from codeboxapi import CodeBox

codebox = CodeBox()
codebox.upload("data.csv", b"1,2,3\
4,5,6")
output = codebox.run("import pandas as pd; df = pd.read_csv('data.csv')")
print(output.content)
```
