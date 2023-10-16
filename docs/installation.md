# Installation
## Install Dependencies

To install, it's recommended to create a virtual environment (using `venv` in the example below):

```bash
python3 -m venv codeinterpreterenv
source codeinterpreterenv/bin/activate
```

Then install the package:

```bash
pip install "codeinterpreterapi[all]"
```

Everything for local experiments are installed with the all extra. For deployments, you can use `pip install codeinterpreterapi` instead which does not install the additional dependencies.

## Set Up Environment Variables


You will also need to configure API keys for the AI model you want to use, either OpenAI, Anthropic, or Azure.

For OpenAI, create a `.env` file with:

```bash
OPENAI_API_KEY=sk-...
```
or export as an environment variable in your terminal:

```bash
export OPENAI_API_KEY=your_openai_api_key
```

For Azure, use:

```bash
OPENAI_API_TYPE=azure
OPENAI_API_VERSION=2023-07-01-preview
OPENAI_API_BASE=
DEPLOYMENT_NAME=
```
