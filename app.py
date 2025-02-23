import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

st.set_page_config(page_title="Okta Auth Demo", page_icon='🔐', initial_sidebar_state="auto", menu_items=None)

if not st.experimental_user.is_logged_in:
    st.button("Log in with Okta", on_click=st.login)
    st.stop()
    
st.button("Log out", on_click=st.logout)
#st.write(st.experimental_user)

# Credits: https://github.com/streamlit/llamaindex-chat-with-streamlit-docs/tree/main
openai.api_key = st.secrets.openai.key
st.title("Identity-Aware Chat Demo (Powered by Okta & OpenAI)")

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

# display info about currently logged in user
st.info(f"Welcome {st.experimental_user.name}! Your Role: {st.experimental_user.job_title}")

with st.expander("See more"):
    st.markdown(  
    """  
    This **demo app** presents a **simple, user identity-aware AI chatbot** using the new **native Streamlit authentication** functionality  
    _(available as of the **1.42.0** release)_, along with **Okta, LlamaIndex, and OpenAI**.  

    ## 🚀 How It Works:  
    - The **Streamlit app** is deployed on **Streamlit Community Cloud** and integrated with an **Okta account** using **OIDC**  
      _(see [docs](https://docs.streamlit.io/develop/concepts/connections/authentication) for details)_.  
    - Only users **assigned to the app** can access it via the **Okta dashboard** after verification with a **password and an Okta Verify code**.  
    - **Metadata** about the currently logged-in user _(e.g., name, email, etc.)_ is available in `st.experimental_user`.  
      This data is **parsed from the ID Token** that Okta sends.  
    - Additional **custom attributes** can be added as **custom claims** in Okta Admin _(see [Okta docs](https://developer.okta.com/docs/guides/customize-tokens-returned-from-okta/main/))_.  
      **⚠️ Note:** To retrieve additional attributes, you **must use a custom authorization server**!  
    - Each user has an attribute:  
      - **`is_manager`** (_boolean_)  
      - **`job_title`**, which in production can be supplied to Okta via **Directory Integration**.  

    ## 💬 Chatbot & Retrieval Setup  
    - A **boilerplate chat interface** is built using **native Streamlit functionality**.  
    - We use **LlamaIndex** with `SimpleDirectoryReader` to set up a **basic RAG pipeline**, which:  
      - **Loads** documents from a directory  
      - **Stores** embeddings in a **local vector store**  
      - **Makes** them available for **LLM querying**  
    - The chatbot uses **GPT-4o-mini** by **OpenAI**.  

    ## 🔐 Role-Based Access Control  
    - The directory contains **sample documentation** about fictional company processes, including:  
      - **HR & IT FAQs**  
      - **Budgeting documents** _(restricted access)_  
    - **Budget information is only accessible to managers**.  
      - 🔹 **If a user is _not_ a manager**, and asks the chatbot about budgeting, they **won't receive any information**  
        _(because the model does not have access to those documents)_.  
      - 🔹 **If a user _is_ a manager**, they **will be able to retrieve budget-related information**.  
    - This access control is enforced using:  
      ```python
      st.experimental_user.is_manager  
      ```  
      to determine the appropriate **document directory path**.  
    """  
)

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
        
