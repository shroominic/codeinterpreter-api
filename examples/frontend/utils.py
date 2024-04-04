import os
import shutil
import tempfile
from typing import Optional

import streamlit as st
from codeinterpreterapi import CodeInterpreterSession


def create_temp_folder() -> str:
    """
    Creates a temp folder
    """
    temp_folder = tempfile.mkdtemp()
    return temp_folder


async def get_images(prompt: str, files: Optional[list] = None) -> list:
    if files is None:
        files = []
    with st.chat_message("user"):  # type: ignore
        st.write(prompt)
    with st.spinner():
        async with CodeInterpreterSession(model="gpt-3.5-turbo") as session:
            response = await session.agenerate_response(prompt, files=files)

            with st.chat_message("assistant"):  # type: ignore
                st.write(response.content)

                # Showing Results
                for _file in response.files:
                    st.image(_file.get_image(), caption=prompt, use_column_width=True)

                # Allowing the download of the results
                if len(response.files) == 1:
                    st.download_button(
                        "Download Results",
                        response.files[0].content,
                        file_name=response.files[0].name,
                    )
                else:
                    target_path = tempfile.mkdtemp()
                    for _file in response.files:
                        _file.save(os.path.join(target_path, _file.name))

                    zip_path = os.path.join(os.path.dirname(target_path), "archive")
                    shutil.make_archive(zip_path, "zip", target_path)

                    with open(zip_path + ".zip", "rb") as f:
                        st.download_button(
                            "Download Results",
                            f,
                            file_name="archive.zip",
                        )
    return response.files
