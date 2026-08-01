import httpx
import traceback

URL = "http://localhost:8000/api/upload-video"
PAYLOAD = {"url": "ENLEjGozrio"}

try:
    r = httpx.post(URL, json=PAYLOAD, timeout=600.0)
    print('STATUS', r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    traceback.print_exc()
    print('ERROR', e)
