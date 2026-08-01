import httpx
import traceback
import os

URL_UPLOAD = 'http://localhost:8000/api/upload-video'
URL_CHAT = 'http://localhost:8000/api/chat'
VIDEO_URL = 'https://www.youtube.com/watch?v=kmsBuHT2kTo'
QUESTION = 'What is the main topic of the video?'

try:
    print('Uploading', VIDEO_URL)
    r = httpx.post(URL_UPLOAD, json={'url': VIDEO_URL}, timeout=600.0)
    print('UPLOAD STATUS', r.status_code)
    try:
        up = r.json()
    except Exception:
        up = {'text': r.text}
    print(up)

    video_id = up.get('video_id') if isinstance(up, dict) else None
    if not video_id:
        # try to extract id from URL
        if 'v=' in VIDEO_URL:
            video_id = VIDEO_URL.split('v=')[-1].split('&')[0]

    payload = {'question': QUESTION, 'video_id': video_id, 'top_k': 5}
    print('Chat payload', payload)
    r2 = httpx.post(URL_CHAT, json=payload, timeout=120.0)
    print('CHAT STATUS', r2.status_code)
    try:
        print(r2.json())
    except Exception:
        print(r2.text)
except Exception as e:
    traceback.print_exc()
    print('ERROR', e)
