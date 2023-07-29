import asyncio
from langchain.chat_models.anthropic import ChatAnthropic
from codeinterpreterapi import CodeInterpreterSession


async def run_with_claude():
    llm = ChatAnthropic(model="claude-2")
    
    async with CodeInterpreterSession(llm=llm) as session:
        result = await session.generate_response(
            "Plot the nvidea stock vs microsoft stock over the last 6 months."
        )
        result.show()
        
        result = await session.generate_response(
            "Store this data to a csv file."
        )
        print(result.files)


if __name__ == "__main__":
    asyncio.run(run_with_claude())
