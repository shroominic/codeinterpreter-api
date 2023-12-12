# Bitcoin Chart

This example creates a CodeInterpreterSession and generates a response to plot the bitcoin chart for year 2023:

```python
from codeinterpreterapi import CodeInterpreterSession

with CodeInterpreterSession() as session:
  response = session.generate_response("Plot the bitcoin chart for year 2023")

print(response.content)
response.files[0].show_image() # Show the chart image
```

The session handles executing the python code to generate the chart in the sandboxed environment. The response contains the chart image that can be displayed.

![Bitcoin Chart Output](https://raw.githubusercontent.com/shroominic/codeinterpreter-api/main/examples/assets/bitcoin_chart.png)
Bitcoin Chart Output
