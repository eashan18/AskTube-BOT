import requests, json, traceback
try:
    r = requests.post('http://127.0.0.1:8000/api/upload-video', json={'url':'https://www.youtube.com/watch?v=ENLEjGozrio'}, timeout=120)
    print(r.status_code)
    print(r.text)
except Exception:
    traceback.print_exc()
