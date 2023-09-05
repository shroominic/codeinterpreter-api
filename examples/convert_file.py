from codeinterpreterapi import CodeInterpreterSession, File

with CodeInterpreterSession() as session:
    user_request = "Convert this dataset to excel."
    files = [
        File.from_path("examples/assets/iris.csv"),
    ]

    response = session.generate_response(user_request, files)

    print("AI: ", response.content)
    for file in response.files:
        if file.name == "iris.xlsx":
            file.save("examples/assets/iris.xlsx")
