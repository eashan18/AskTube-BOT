import os
import httpx

base = os.getenv('GROQ_BASE_URL', 'https://api.groq.com')
key = os.getenv('GROQ_API_KEY')
url = base.rstrip('/') + '/openai/v1/responses'
payload = {'model': 'openai/gpt-oss-20b', 'input': 'Say hello in one sentence'}
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

print('POST', url)
try:
    r = httpx.post(url, json=payload, headers=headers, timeout=15.0)
    print('STATUS', r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
