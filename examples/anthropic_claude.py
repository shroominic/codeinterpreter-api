import asyncio
from langchain.chat_models.anthropic import ChatAnthropic
from codeinterpreterapi import CodeInterpreterSession


async def run_with_claude():
    llm = ChatAnthropic(model="claude-2")
    
    async with CodeInterpreterSession(llm=llm) as session:
        prompt = "Plot the nvidea stock vs microsoft stock over the last 6 months. "

        result = await session.generate_response(prompt)
    
        print("AI: ", result.content)
        for file in result.files:
            file.show_image()


if __name__ == "__main__":
    asyncio.run(run_with_claude())
