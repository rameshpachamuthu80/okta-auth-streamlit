import streamlit as st

if not st.experimental_user.is_logged_in:
    st.button("Log in with Okta", on_click=st.login)
    st.stop()

st.button("Log out", on_click=st.logout)
#st.write(st.experimental_user)
st.write(f"Welcome {st.experimental_user.name}!")
st.write(f"Role: {st.experimental_user.job_title}!")


