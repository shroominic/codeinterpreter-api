from codeinterpreterapi import CodeInterpreterSession
import streamlit as st


async def get_images(prompt: str):
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner():
        async with CodeInterpreterSession(model='gpt-3.5-turbo') as session:
            response = await session.generate_response(
                prompt
            )

            with st.chat_message("assistant"):
                st.write(response.content)

                for file in response.files:
                    st.image(file.get_image(), caption=prompt, use_column_width=True)