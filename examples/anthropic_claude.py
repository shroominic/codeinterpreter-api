from codeinterpreterapi import CodeInterpreterSession

with CodeInterpreterSession(model="claude-3-haiku-20240307") as session:
    result = session.generate_response("Plot the nvidea stock vs microsoft stock over the last 6 months.")
    result.show()
