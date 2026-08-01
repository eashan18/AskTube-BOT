import httpx

URL_CHAT = 'http://localhost:8000/api/chat'
payload = {'question': 'What is the main topic of the video?', 'video_id': 'kmsBuHT2kTo', 'top_k': 3}
try:
    r = httpx.post(URL_CHAT, json=payload, timeout=120.0)
    print('STATUS', r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
