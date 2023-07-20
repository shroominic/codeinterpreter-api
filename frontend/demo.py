import asyncio

import streamlit as st

from codeinterpreterapi import File
from frontend.utils import get_images

st.title('Code Interpreter API 🚀')

# This will create a sidebar
st.sidebar.title("Code Interpreter API 🚀")
st.sidebar.markdown("[Github Repo](https://github.com/shroominic/codeinterpreter-api)")


# This will create a textbox where you can input text
input_text = st.text_area("Write your prompt")
uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True,
                                  type=".csv")

uploaded_files_list = []
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    uploaded_files_list.append(File.from_bytes(name=uploaded_file.name,
                                               content=bytes_data))

# This will create a button
button_pressed = st.button('Run code interpreter', use_container_width=True)

# This will display the image only when the button is pressed
if button_pressed and input_text != "":
    asyncio.run(get_images(input_text, files=uploaded_files_list))
