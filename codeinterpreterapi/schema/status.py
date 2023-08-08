from codeboxapi.schema import CodeBoxStatus  # type: ignore


class SessionStatus(CodeBoxStatus):
    @classmethod
    def from_codebox_status(cls, cbs: CodeBoxStatus) -> "SessionStatus":
        return cls(status=cbs.status)

    def __repr__(self):
        return f"<SessionStatus status={self.status}>"
