from langchain_core.prompts import PromptTemplate

determine_modifications_prompt = PromptTemplate(
    input_variables=["code"],
    template="The user will input some code and you need to determine "
    "if the code makes any changes to the file system. \n"
    "With changes it means creating new files or modifying existing ones.\n"
    "Format your answer as JSON inside a codeblock with a "
    "list of filenames that are modified by the code.\n"
    "If the code does not make any changes to the file system, "
    "return an empty list.\n\n"
    "Determine modifications:\n"
    "```python\n"
    "import matplotlib.pyplot as plt\n"
    "import numpy as np\n\n"
    "t = np.arange(0.0, 4.0*np.pi, 0.1)\n\n"
    "s = np.sin(t)\n\n"
    "fig, ax = plt.subplots()\n\n"
    "ax.plot(t, s)\n\n"
    'ax.set(xlabel="time (s)", ylabel="sin(t)",\n'
    '   title="Simple Sin Wave")\n'
    "ax.grid()\n\n"
    'plt.savefig("sin_wave.png")\n'
    "```\n\n"
    "Answer:\n"
    "```json\n"
    "{{\n"
    '  "modifications": ["sin_wave.png"]\n'
    "}}\n"
    "```\n\n"
    "Determine modifications:\n"
    "```python\n"
    "import matplotlib.pyplot as plt\n"
    "import numpy as np\n\n"
    "x = np.linspace(0, 10, 100)\n"
    "y = x**2\n\n"
    "plt.figure(figsize=(8, 6))\n"
    "plt.plot(x, y)\n"
    'plt.title("Simple Quadratic Function")\n'
    'plt.xlabel("x")\n'
    'plt.ylabel("y = x^2")\n'
    "plt.grid(True)\n"
    "plt.show()\n"
    "```\n\n"
    "Answer:\n"
    "```json\n"
    "{{\n"
    '  "modifications": []\n'
    "}}\n"
    "```\n\n"
    "Determine modifications:\n"
    "```python\n"
    "{code}\n"
    "```\n\n"
    "Answer:\n"
    "```json\n",
)
