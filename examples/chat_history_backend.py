import os

os.environ["HISTORY_BACKEND"] = "redis"
os.environ["REDIS_HOST"] = "redis://localhost:6379"

from codeinterpreterapi import CodeInterpreterSession  # noqa: E402


def main() -> None:
    session_id = None

    session = CodeInterpreterSession()
    session.start()

    print("Session ID:", session.session_id)
    session_id = session.session_id

    response = session.generate_response("Plot the bitcoin chart of 2023 YTD")
    response.show()

    del session

    assert session_id is not None
    session = CodeInterpreterSession.from_id(session_id)

    response = session.generate_response("Now for the last 5 years")
    response.show()

    session.stop()


if __name__ == "__main__":
    main()
