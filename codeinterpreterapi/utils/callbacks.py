from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import AgentAction

if TYPE_CHECKING:
    from codeinterpreterapi.session import CodeInterpreterSession


class CodeCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self, session: "CodeInterpreterSession"):
        self.session = session
        super().__init__()

    async def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run on agent action."""
        if action.tool == "python":
            await self.session.show_code(
                "⚙️ Running code: "
                f"```python\n{action.tool_input['code']}\n```"  # type: ignore
            )
        else:
            raise ValueError(f"Unknown action: {action.tool}")
