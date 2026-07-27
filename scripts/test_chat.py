from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
resp = client.post('/api/chat', json={'question': 'What is the main topic of the video?', 'video_id': 'ENLEjGozrio', 'top_k': 5})
print('status', resp.status_code)
print(resp.json())
