from codeinterpreterapi import CodeInterpreterSession, File


class CodeInterpreter:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def process(self, prompt, uploaded_files):
        files = []
        for uploaded_file in uploaded_files:
            file = File(name=uploaded_file.name, content=uploaded_file.read())
            files.append(file)
        async with CodeInterpreterSession(model="gpt-3.5-turbo") as session:
            response = await session.generate_response(
                prompt, files=files, detailed_error=True
            )
            return response
