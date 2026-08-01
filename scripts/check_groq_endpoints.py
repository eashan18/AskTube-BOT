import httpx
import os

key = os.getenv('GROQ_API_KEY')
base = os.getenv('GROQ_BASE_URL', 'https://api.groq.com')
model = 'llama-3.3-70b'
prompt = 'Say hello'

def try_endpoint(path, payload):
    url = base.rstrip('/') + path
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    try:
        r = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        print(url, r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:1000])
    except Exception as e:
        print(url, 'ERROR', e)

# common payloads
payload_a = { 'model': model, 'prompt': prompt, 'max_tokens': 50 }
payload_b = { 'model': model, 'messages': [{'role':'user','content':prompt}], 'max_tokens':50 }

try_endpoint('/v1/generate', payload_a)
try_endpoint('/v1/completions', payload_a)
try_endpoint('/v1/completions', payload_b)
try_endpoint(f'/v1/models/{model}/outputs', payload_b)
