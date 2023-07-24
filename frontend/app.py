import asyncio
import streamlit as st
from codeinterpreterapi.config import settings
from codeinterpreterapi import CodeInterpreterSession
from codeinterpreterapi.schema.file import File


async def main():
    # App title
    st.set_page_config(page_title="Code Interpreter API 🚀",
                    layout="wide")
    # Replicate Credentials
    with st.sidebar:
        st.title('Code Interpreter API 🚀')
        if settings.OPENAI_API_KEY is not None:
            st.success('OpenAI API key already provided!', icon='✅')
        else:
            openai_api = st.text_input('Enter your OpenAI API token:', type='password')
            if not openai_api.startswith('sk'):
                st.warning('Please enter your credentials!', icon='⚠️')
            else:
                settings.OPENAI_API_KEY = openai_api
                st.success('Proceed to entering your prompt message!', icon='👉')
                st.experimental_rerun()
    
        st.markdown('📖 Learn more [here](https://github.com/shroominic/codeinterpreter-api)')

        uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

        uploaded_files_list = []
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
            uploaded_files_list.append(File(name=uploaded_file.name,
                                            content=bytes_data))

    if settings.OPENAI_API_KEY is not None:
        session = st.session_state["session"]
        # Store LLM generated responses
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?",
                                        "images": [], "captions": []}]

  
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                for i, image in enumerate(message["images"]):
                    st.image(image, caption=message["captions"][i], use_column_width=True)
            
        # Display or clear chat messages
        def clear_chat_history():
            st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?",
                                        "images": [], "captions": []}]
            st.session_state["session"].astop()
            del st.session_state['session']
        st.sidebar.button('Clear Chat History', on_click=clear_chat_history,
                          use_container_width=True)


        # User-provided prompt
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user",
                                            "content": prompt,
                                            "images": [],
                                            "captions": []})
            with st.chat_message("user"):
                st.write(prompt)

        # Generate a new response if last message is not from assistant
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = await session.generate_response(
                    prompt,
                    files=uploaded_files_list,
                    detailed_error=False,
                    )
                    st.write(response.content)

                    _imgs = []
                    _captions = []
                    # Showing Results
                    for _file in response.files:
                        _img = _file.get_image()
                        st.image(_img, caption=prompt, use_column_width=True)
                        _imgs.append(_img)
                        _captions.append(prompt)


                message = {"role": "assistant", "content": response.content,
                           "images": _imgs, "captions": _captions}
                
                
            st.session_state.messages.append(message)
            


if "session" not in st.session_state and settings.OPENAI_API_KEY is not None:
    async def get_session():
        async with CodeInterpreterSession(model='gpt-3.5-turbo',
                                          openai_api_key=settings.OPENAI_API_KEY) as session:
            st.session_state['session'] = session
    
    asyncio.run(get_session())


asyncio.run(main())