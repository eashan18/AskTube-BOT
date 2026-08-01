import streamlit as st
import httpx
import os
from typing import List, Dict, Any

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


def header():
    st.title("AskTube AI — Chat with Any YouTube Video")
    st.markdown(
        "Ask questions about the content of uploaded YouTube videos. "
        "Answers are generated from indexed transcripts and include citation details."
    )


def home_page():
    header()
    st.header("Welcome")
    st.markdown(
        "Use the Upload page to index a YouTube video, then ask questions on the Chat page. "
        "The app normalizes YouTube URLs and strips playlist/query parameters automatically."
    )
    st.info("Upload a video using the full URL, then use the Chat page to query the indexed content.")


def upload_page():
    header()
    st.header("Upload Video")

    url = st.text_input("YouTube URL or ID", placeholder="https://www.youtube.com/watch?v=VIDEO_ID")
    if st.button("Upload and Index"):
        if not url:
            st.error("Provide a YouTube URL or video ID.")
        else:
            with st.spinner("Processing video — this can take a minute..."):
                try:
                    resp = httpx.post(f"{API_BASE}/upload-video", json={"url": url}, timeout=600.0)
                    resp.raise_for_status()
                    data = resp.json()
                    st.success(
                        f"Indexed video: {data.get('title')} (id: {data.get('video_id')}) — chunks indexed: {data.get('chunks_indexed')}"
                    )
                    st.session_state["last_video_id"] = data.get("video_id")
                    st.session_state["last_video_title"] = data.get("title")
                except httpx.HTTPStatusError as exc:
                    message = exc.response.text if exc.response is not None else str(exc)
                    st.error(f"Upload failed: {message}")
                except Exception as exc:
                    st.error(f"Upload failed: {exc}")

    if st.session_state.get("last_video_id"):
        st.markdown("---")
        st.subheader("Last Uploaded Video")
        st.write(f"**Video ID:** {st.session_state.get('last_video_id')}  ")
        st.write(f"**Title:** {st.session_state.get('last_video_title')}  ")


def chat_page():
    header()
    st.header("Chat")

    if "last_video_id" not in st.session_state:
        st.info("Upload a video first or enter a Video ID below.")

    col1, col2 = st.columns([3, 1])
    with col1:
        question = st.text_area("Ask a question about the selected video(s)", height=150)
    with col2:
        video_id = st.text_input(
            "Video ID (leave empty to search all)",
            value=st.session_state.get("last_video_id", ""),
            placeholder="Leave empty to search all indexed videos",
        )
        top_k = st.number_input("Top K", min_value=1, max_value=20, value=5)

    if st.button("Ask"):
        if not question:
            st.error("Enter a question.")
        else:
            with st.spinner("Retrieving and generating answer..."):
                try:
                    payload = {"question": question, "video_id": video_id or None, "top_k": top_k}
                    resp = httpx.post(f"{API_BASE}/chat", json=payload, timeout=120.0)
                    resp.raise_for_status()
                    data = resp.json()
                    answer = data.get("answer") or "No answer returned. Please try again."

                    st.markdown("### Final Answer")
                    st.success(answer)

                    st.markdown("### Citations")
                    citations = data.get("citations") or []
                    if citations:
                        for c in citations:
                            meta = c.get("metadata", {})
                            st.write(
                                f"- {c.get('id')} — video: {meta.get('video_id')} "
                                f"[{meta.get('start_timestamp')}-{meta.get('end_timestamp')}]"
                            )
                    else:
                        st.write("No citations returned.")

                    retrieved = data.get("retrieved_chunks") or []
                    if retrieved:
                        with st.expander("Show retrieved chunks", expanded=False):
                            for rc in retrieved:
                                meta = rc.get("metadata", {})
                                st.write(
                                    f"**{rc.get('id')}** — video: {meta.get('video_id')} "
                                    f"[{meta.get('start_timestamp')}-{meta.get('end_timestamp')}]"
                                )
                                st.write(rc.get("document") or rc.get("content") or meta.get("original_text", ""))
                    else:
                        st.write("No retrieved chunks returned.")

                    history = st.session_state.get("history", [])
                    history.insert(0, {"question": question, "answer": answer})
                    st.session_state["history"] = history
                except httpx.HTTPStatusError as exc:
                    message = exc.response.text if exc.response is not None else str(exc)
                    st.error(f"Chat failed: {message}")
                except Exception as exc:
                    st.error(f"Chat failed: {exc}")


def history_page():
    header()
    st.header("History")

    if st.button("Clear session history"):
        st.session_state["history"] = []
        st.success("Session history cleared.")

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
