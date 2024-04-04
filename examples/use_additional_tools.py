"""
The exciting part about this example is
that the code interpreter has internet access
so it can download the bitcoin chart from yahoo finance
and plot it for you
"""
import csv
import io
from typing import Any

from codeinterpreterapi import CodeInterpreterSession
from langchain_core.tools import BaseTool


class ExampleKnowledgeBaseTool(BaseTool):
    name: str = "salary_database"
    description: str = "Use to get salary data of company employees"

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        f = io.StringIO()
        writer = csv.writer(f)
        writer.writerow(["month", "employee", "salary"])
        writer.writerow(["march 2022", "Jan", "1200"])
        writer.writerow(["march 2022", "Ola", "1500"])
        writer.writerow(["april 2022", "Jan", "1800"])
        writer.writerow(["april 2022", "Ola", "2000"])
        return f.getvalue()


async def main() -> None:
    async with CodeInterpreterSession(
        additional_tools=[ExampleKnowledgeBaseTool()]
    ) as session:
        response = await session.agenerate_response(
            "Plot chart of company employee salaries"
        )

        response.show()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
