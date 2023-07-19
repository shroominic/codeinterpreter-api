import asyncio

import streamlit as st

from frontend.utils import get_images

st.title('Code Interpreter API 🚀')

# This will create a sidebar
st.sidebar.title("Code Interpreter API 🚀")
st.sidebar.markdown("[Github Repo](https://github.com/shroominic/codeinterpreter-api)")


# This will create a textbox where you can input text
input_text = st.text_input("Write your prompt")

# This will create a button
button_pressed = st.button('Run code interpreter', use_container_width=True)

# This will display the image only when the button is pressed
if button_pressed and input_text != "":
    asyncio.run(get_images(input_text))
