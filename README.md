# Identity-aware chatbot (Streamlit, Okta & OpenAI)

This repository presents a simple, user identity-aware AI chatbot using the new native Streamlit authentication
_(available as of Streamlit 1.42.0)_ with Okta, LlamaIndex, and OpenAI.

## Features  
- **Native Streamlit authentication** using Okta  
- **Role-based access control (RBAC)** for document retrieval  
- **LlamaIndex-powered** RAG pipeline for document-based chatbot responses  
- **Integration with OpenAI's GPT-4o-mini**  
- **Streamlit Community Cloud deployment**

## How It Works  

### 1. Authentication & User Metadata  
- The Streamlit app is deployed on Streamlit Community Cloud and integrates with an Okta account via OIDC.  
- Only users assigned to the app can access it through the Okta dashboard after verification with a password and Okta Verify code.  
- User metadata _(e.g., name, email, etc.)_ is available in:  
  ```python
  st.experimental_user
  ```
  This metadata is parsed from the ID Token provided by Okta.

### 2. Custom Attributes in Okta
- Additional custom attributes (e.g., is_manager, job_title) can be added as custom claims in Okta Admin.

Note: To retrieve additional attributes, you must use a custom authorization server.

### 3. AI Chatbot & RAG Pipeline
- A boilerplate chat interface is built using native Streamlit functionality.
- The chatbot uses LlamaIndex with SimpleDirectoryReader to create a RAG pipeline:
  Loads documents from a directory
  Stores embeddings in a local vector store
  Enables LLM-based querying
- GPT-4o-mini by OpenAI is used as the language model.

### 4. Role-Based Access Control
The chatbot retrieves documents based on user roles:

- HR & IT FAQs document → Available to all users
- Budgeting document → Only available to managers

  How access control is enforced:
    ```python
  if st.experimental_user.is_manager:
    # Load budget-related documents
  else:
    # Restrict access
  ```
- Non-managers cannot access budget information.

## Installation & Setup
Prerequisites: 
- Python 3.9+
- Streamlit 1.42.0+
- Okta Developer Account
- OpenAI API Key

Install Dependencies:
```python
pip install requirements.txt
```

### Configuring Secrets
Navigate to your project directory and create a .streamlit folder. Inside the .streamlit folder, create a secrets.toml file.

Open the secrets.toml file in a text editor and add the following content:
```python
[openai]
key = ""  # Your OpenAI API key

[auth]
redirect_uri = "https://your_app_url/oauth2callback"
cookie_secret = "random secret"  # Replace with a secure random string
client_id = ""  # Okta Client ID
client_secret = ""  # Okta Client Secret
server_metadata_url = ""  # Okta Authorization Server Metadata URL
```

⚠️ Ensure secrets.toml is ignored in Git!
