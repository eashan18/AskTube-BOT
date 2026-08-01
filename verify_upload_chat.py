import os
import sys
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
url = "https://www.youtube.com/watch?v=Hk-Wop82dEE"
print("UPLOAD URL:", url)
up = client.post("/api/upload-video", json={"url": url})
print("UPLOAD", up.status_code)
print(up.text)
if up.status_code == 200:
    vid = up.json().get("video_id", "Hk-Wop82dEE")
    chat = client.post(
        "/api/chat",
        json={"question": "What is the main topic of this video?", "video_id": vid, "top_k": 5},
    )
    print("CHAT", chat.status_code)
    print(chat.json())
else:
    print("Upload failed; chat skipped.")
