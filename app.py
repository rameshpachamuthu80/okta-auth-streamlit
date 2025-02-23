import streamlit as st
import jwt

if not st.experimental_user.is_logged_in:
    st.button("Log in with Okta", on_click=st.login)
    st.stop()

st.button("Log out", on_click=st.logout)
st.write(st.experimental_user)


