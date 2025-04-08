import streamlit as st

st.set_page_config(page_title="Okta Auth Demo", page_icon='🔐', initial_sidebar_state="auto", menu_items=None)

if not st.experimental_user.is_logged_in:
    st.login()
    st.stop()
