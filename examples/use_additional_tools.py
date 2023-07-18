"""
The exciting part about this example is
that the code interpreter has internet access
so it can download the bitcoin chart from yahoo finance
and plot it for you
"""
import csv
import io
from datetime import datetime
from typing import Any

from langchain.tools import tool, BaseTool

from codeinterpreterapi import CodeInterpreterSession


class ExampleKnowledgeBaseTool(BaseTool):
    name = "salary_database"
    description = "Use to get salary data of company employees"

    def _run(self, *args, **kwargs):
        raise NotImplementedError()

    async def _arun(self, *args, **kwargs: Any) -> Any:
        f = io.StringIO()
        writer = csv.writer(f)
        writer.writerow(['month', 'employee', 'salary'])
        writer.writerow(['march 2022', 'Jan', '1200'])
        writer.writerow(['march 2022', 'Ola', '1500'])
        writer.writerow(['april 2022', 'Jan', '1800'])
        writer.writerow(['april 2022', 'Ola', '2000'])
        return f.getvalue()


async def main():
    async with CodeInterpreterSession(tools=[ExampleKnowledgeBaseTool()]) as session:
        response = await session.generate_response(
            f"Plot chart of company employee salaries"
        )

        print("AI: ", response.content)
        for file in response.files:
            file.show_image()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
