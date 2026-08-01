from fastapi.testclient import TestClient
from backend.main import app
import json

client = TestClient(app)

print('=== Upload Video ===')
upload_resp = client.post('/api/upload-video', json={'url': 'https://www.youtube.com/watch?v=ENLEjGozrio'}, timeout=600)
print('UPLOAD STATUS:', upload_resp.status_code)
try:
    print('UPLOAD JSON:', json.dumps(upload_resp.json(), indent=2))
except Exception as e:
    print('UPLOAD PARSE ERROR:', e)
    print(upload_resp.text)

video_id = 'ENLEjGozrio'
if upload_resp.status_code == 200:
    try:
        data = upload_resp.json()
        video_id = data.get('video_id', video_id)
    except Exception:
        pass

print('\n=== Chat Request ===')
chat_resp = client.post('/api/chat', json={'question': 'What is the main topic of the video?', 'video_id': video_id, 'top_k': 5}, timeout=600)
print('CHAT STATUS:', chat_resp.status_code)
try:
    print('CHAT JSON:', json.dumps(chat_resp.json(), indent=2))
except Exception as e:
    print('CHAT PARSE ERROR:', e)
    print(chat_resp.text)
