from asyncio import run as _await

from codeinterpreterapi.chains import (
    aget_file_modifications,
    aremove_download_link,
    get_file_modifications,
    remove_download_link,
)
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")

remove_download_link_example = (
    "I have created the plot to your dataset.\n\n"
    "Link to the file [here](sandbox:/plot.png)."
)

base_code = """
    import matplotlib.pyplot as plt

    x = list(range(1, 11))
    y = [29, 39, 23, 32, 4, 43, 43, 23, 43, 77]

    plt.plot(x, y, marker='o')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Data Plot')
    """
code_with_mod = base_code + "\nplt.savefig('plot.png')"

code_no_mod = base_code + "\nplt.show()"


def test_remove_download_link() -> None:
    assert (
        remove_download_link(remove_download_link_example, llm=llm).strip()
        == "I have created the plot to your dataset."
    )


def test_remove_download_link_async() -> None:
    assert (
        _await(aremove_download_link(remove_download_link_example, llm=llm))
    ).strip() == "I have created the plot to your dataset."


def test_get_file_modifications() -> None:
    assert get_file_modifications(code_with_mod, llm=llm) == ["plot.png"]
    assert get_file_modifications(code_no_mod, llm=llm) == []


def test_get_file_modifications_async() -> None:
    assert _await(aget_file_modifications(code_with_mod, llm=llm)) == ["plot.png"]
    assert _await(aget_file_modifications(code_no_mod, llm=llm)) == []


if __name__ == "__main__":
    test_remove_download_link()
    test_remove_download_link_async()
    test_get_file_modifications()
    test_get_file_modifications_async()
