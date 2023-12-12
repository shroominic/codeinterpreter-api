from datetime import datetime

from codeinterpreterapi import CodeInterpreterSession


def main() -> None:
    with CodeInterpreterSession(local=True) as session:
        currentdate = datetime.now().strftime("%Y-%m-%d")

        response = session.generate_response(
            f"Plot the bitcoin chart of 2023 YTD (today is {currentdate})"
        )

        # prints the text and shows the image
        response.show()


if __name__ == "__main__":
    main()
