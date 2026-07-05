"""
Chat interface page: handles document upload and the interactive RAG chat.
"""
import streamlit as st

from utils.api_client import send_query, upload_document

st.set_page_config(page_title="Chat - Adaptive RAG", page_icon="💬", layout="wide")

if not st.session_state.get("session_id"):
    st.warning("Please start a session on the Home page first.")
    st.stop()

st.title("💬 Adaptive RAG Chat")
st.caption(f"Session: `{st.session_state.session_id}`")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📄 Upload Documents")
    uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
    description = st.text_input("Document description", placeholder="e.g. Q3 financial report")

    if st.button("Upload & Index", disabled=not uploaded_file):
        if not description.strip():
            st.error("Please provide a description.")
        else:
            with st.spinner("Processing and indexing document..."):
                try:
                    result = upload_document(uploaded_file.read(), uploaded_file.name, description)
                    if result.get("status"):
                        st.success(f"'{uploaded_file.name}' indexed successfully.")
                    else:
                        st.error("Upload failed.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Upload error: {exc}")

    st.divider()
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = send_query(prompt, st.session_state.session_id)
                answer = response.get("result", {}).get("content", "No response received.")
            except Exception as exc:  # noqa: BLE001
                answer = f"Error contacting backend: {exc}"
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
