import httpx
import traceback

URL = "http://localhost:8000/api/health"

try:
    r = httpx.get(URL, timeout=10.0)
    print("STATUS", r.status_code)
    print(r.text)
except Exception as e:
    traceback.print_exc()
    print("ERROR", e)
