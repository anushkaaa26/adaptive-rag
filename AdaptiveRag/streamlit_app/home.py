"""
Streamlit entry point: real login/registration page (backed by the FastAPI
/auth endpoints) for the Adaptive RAG chatbot.
"""
import uuid

import streamlit as st

from utils.api_client import check_health, login, register

st.set_page_config(page_title="Adaptive RAG Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Adaptive RAG - Agentic AI Chatbot")
st.write("Sign in or create an account to start chatting with your documents.")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "username" not in st.session_state:
    st.session_state.username = None

backend_ok = check_health()
if backend_ok:
    st.success("Backend is reachable.")
else:
    st.warning("Backend is not reachable -- start the FastAPI server first.")

if st.session_state.username:
    st.info(f"Logged in as **{st.session_state.username}**")
    st.caption(f"Session ID: `{st.session_state.session_id}`")
    st.page_link("pages/chat.py", label="Go to Chat", icon="💬")
    if st.button("Log out"):
        st.session_state.username = None
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()
else:
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not username.strip() or not password:
                    st.error("Please enter both a username and password.")
                else:
                    ok, message = login(username, password)
                    if ok:
                        st.session_state.username = username.strip().lower()
                        st.session_state.session_id = f"{st.session_state.username}_{uuid.uuid4().hex[:8]}"
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose a username", key="reg_username")
            new_password = st.text_input(
                "Choose a password (min 6 characters)", type="password", key="reg_password"
            )
            reg_submitted = st.form_submit_button("Create account")

            if reg_submitted:
                if not new_username.strip() or len(new_password) < 6:
                    st.error("Username is required and password must be at least 6 characters.")
                else:
                    ok, message = register(new_username, new_password)
                    if ok:
                        st.success(f"{message} You can now log in.")
                    else:
                        st.error(message)
