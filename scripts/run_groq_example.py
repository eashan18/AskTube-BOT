from backend.services.llm_client import LLMClient

prompt = "Summarize: The quick brown fox jumps over the lazy dog. Keep it short."
client = LLMClient()
print('mock_mode', client.mock_mode)
try:
    resp = client.generate(prompt=prompt, model='llama-3.3-70b', temperature=0.0, max_tokens=200)
    import json
    print('raw_response:')
    print(json.dumps(resp, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
