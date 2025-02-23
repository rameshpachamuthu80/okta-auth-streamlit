import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings


st.set_page_config(page_title="Okta Auth Demo", layout="centered", initial_sidebar_state="auto", menu_items=None)

if not st.experimental_user.is_logged_in:
    st.button("Log in with Okta", on_click=st.login)
    st.stop()


st.button("Log out", on_click=st.logout)
#st.write(st.experimental_user)

# Credits: https://github.com/streamlit/llamaindex-chat-with-streamlit-docs/tree/main
openai.api_key = st.secrets.openai.key
st.title("Identity-Aware Chat Demo")
st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

col1, col2 = st.columns(2)

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me a question!",
        }
    ]

@st.cache_resource(show_spinner=False)
def load_data(dir):
    reader = SimpleDirectoryReader(input_dir=dir, recursive=True)
    docs = reader.load_data()
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        system_prompt="""Your job is to answer employee questions about Stark Industries internal processes. 
        Use the provided documentation, and do not generate information beyond what is available. If you do not know the answer, admit it. 
        Be detailed and helpful in your response. Where applicable, provide contact details such as phone numbers or email addresses from the documentation.""",
    )
    index = VectorStoreIndex.from_documents(docs)
    return index

# define path to docs based on user "is_manager" attribute sent from Okta
if st.experimental_user.is_manager:
    dir = "./data/mng_docs"
else:
    dir = "./data/emp_docs"

index = load_data(dir)

with col1:
    st.write(f"Welcome {st.experimental_user.name}!")
    st.write(f"Your Role: {st.experimental_user.job_title}")

with col2:
    if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(
            chat_mode="condense_question", verbose=True, streaming=True
        )
    
    if prompt := st.chat_input(
        "Ask a question"
    ):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
    
    for message in st.session_state.messages:  # Write message history to UI
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response_stream = st.session_state.chat_engine.stream_chat(prompt)
            st.write_stream(response_stream.response_gen)
            message = {"role": "assistant", "content": response_stream.response}
            # Add response to message history
            st.session_state.messages.append(message)


