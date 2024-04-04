import asyncio
import json
from typing import List

from codeboxapi import CodeBox
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict


class CodeBoxChatMessageHistory(BaseChatMessageHistory):
    """
    Chat message history that stores history inside the codebox.
    """

    def __init__(self, codebox: CodeBox):
        self.codebox = codebox

        if "history.json" not in [f.name for f in self.codebox.list_files()]:
            name, content = "history.json", b"{}"
            if (loop := asyncio.get_event_loop()).is_running():
                loop.create_task(self.codebox.aupload(name, content))
            else:
                self.codebox.upload(name, content)

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from the codebox"""
        msgs = (
            messages_from_dict(json.loads(file_content.decode("utf-8")))
            if (
                file_content := (
                    loop.run_until_complete(self.codebox.adownload("history.json"))
                    if (loop := asyncio.get_event_loop()).is_running()
                    else self.codebox.download("history.json")
                ).content
            )
            else []
        )
        return msgs

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in the local file"""
        print("Current messages: ", self.messages)
        messages = messages_to_dict(self.messages)
        print("Adding message: ", message)
        messages.append(messages_to_dict([message])[0])
        name, content = "history.json", json.dumps(messages).encode("utf-8")
        if (loop := asyncio.get_event_loop()).is_running():
            loop.create_task(self.codebox.aupload(name, content))
        else:
            self.codebox.upload(name, content)
        print("New messages: ", self.messages)

    def clear(self) -> None:
        """Clear session memory from the local file"""
        print("Clearing history CLEARING HISTORY")
        code = "import os; os.remove('history.json')"
        if (loop := asyncio.get_event_loop()).is_running():
            loop.create_task(self.codebox.arun(code))
        else:
            self.codebox.run(code)
