import streamlit as st
import httpx
import os
from typing import List, Dict, Any

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


def header():
    st.title("AskTube AI — Chat with Any YouTube Video")
    st.markdown("Ask questions about the content of uploaded YouTube videos. Answers come only from the uploaded videos.")


def home_page():
    header()
    st.header("Welcome")
    st.info("Use the Upload page to add YouTube videos, then ask questions on the Chat page.")


def upload_page():
    header()
    st.header("Upload Video")

    url = st.text_input("YouTube URL or ID")
    if st.button("Upload and Index"):
        if not url:
            st.error("Provide a YouTube URL or video ID")
        else:
            with st.spinner("Processing video — this may take a while..."):
                try:
                    resp = httpx.post(f"{API_BASE}/upload-video", json={"url": url}, timeout=600.0)
                    resp.raise_for_status()
                    data = resp.json()
                    st.success(f"Indexed video: {data.get('title')} (id: {data.get('video_id')}) — chunks indexed: {data.get('chunks_indexed')}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")


def chat_page():
    header()
    st.header("Chat")

    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_area("Ask a question about the selected video(s)", height=120)
    with col2:
        video_id = st.text_input("Video ID (leave empty to search all)")
        top_k = st.number_input("Top K", min_value=1, max_value=20, value=5)

    if st.button("Ask"):
        if not question:
            st.error("Enter a question")
        else:
            with st.spinner("Retrieving and generating answer..."):
                try:
                    payload = {"question": question, "video_id": video_id or None, "top_k": top_k}
                    resp = httpx.post(f"{API_BASE}/chat", json=payload, timeout=120.0)
                    resp.raise_for_status()
                    data = resp.json()
                    st.markdown("### Answer")
                    st.write(data.get("answer"))

                    st.markdown("### Citations")
                    for c in data.get("citations", []):
                        st.write(c)

                    st.markdown("### Retrieved Chunks")
                    for rc in data.get("retrieved_chunks", []):
                        meta = rc.get("metadata", {})
                        st.write(f"- {rc.get('id')} — video: {meta.get('video_id')} [{meta.get('start_timestamp')}-{meta.get('end_timestamp')}]\n  {rc.get('document')}")

                    # store in session history
                    history = st.session_state.get("history", [])
                    history.insert(0, {"question": question, "answer": data.get("answer")})
                    st.session_state["history"] = history
                except Exception as e:
                    st.error(f"Chat failed: {e}")


def history_page():
    header()
    st.header("History")
    history: List[Dict[str, Any]] = st.session_state.get("history", [])
    if not history:
        st.info("No chat history in this session.")
        return
    for i, item in enumerate(history, start=1):
        with st.expander(f"Q{i}: {item.get('question')}"):
            st.write(item.get("answer"))


def settings_page():
    header()
    st.header("Settings")
    st.info("Settings in this demo are stored via environment variables. Change on the backend configuration or .env file.")


def admin_page():
    header()
    st.header("Admin")
    try:
        resp = httpx.get(f"{API_BASE}/health", timeout=10.0)
        resp.raise_for_status()
        st.success("Backend healthy")
    except Exception as e:
        st.error(f"Backend health check failed: {e}")


def main():
    st.set_page_config(page_title="AskTube AI", layout="wide")

    if "history" not in st.session_state:
        st.session_state["history"] = []

    pages = {
        "Home": home_page,
        "Upload Video": upload_page,
        "Chat": chat_page,
        "History": history_page,
        "Settings": settings_page,
        "Admin": admin_page,
    }

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    pages[choice]()


if __name__ == "__main__":
    main()
