from codeinterpreterapi import CodeInterpreterSession

with CodeInterpreterSession(model="claude-2") as session:
    result = session.generate_response(
        "Plot the nvidea stock vs microsoft stock over the last 6 months."
    )
    result.show()
