import streamlit as st


st.title("Okta Auth Demo")

if not st.experimental_user.is_logged_in:
    st.login()
else:
    st.logout()
  
