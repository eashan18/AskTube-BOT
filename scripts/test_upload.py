import json, urllib.request, traceback
url='http://127.0.0.1:8000/api/upload-video'
data=json.dumps({"url":"https://www.youtube.com/watch?v=ENLEjGozrio"}).encode('utf-8')
req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
try:
    resp=urllib.request.urlopen(req, timeout=120)
    print('status', resp.status)
    print(resp.read().decode())
except Exception as e:
    traceback.print_exc()
