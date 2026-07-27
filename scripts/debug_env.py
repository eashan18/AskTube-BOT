import os
from pathlib import Path
from backend.config.settings import _load_env_file

print('before', repr(os.environ.get('GROQ_API_KEY')))

path = Path('.env')
print('env path', path.resolve(), 'exists', path.exists())
with path.open('r', encoding='utf-8') as handle:
    for line in handle:
        stripped = line.strip()
        print('line repr', repr(line), 'stripped repr', repr(stripped))
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, value = stripped.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        existing = os.environ.get(key)
        print('parsed', key, repr(value), 'existing', repr(existing))
        if key and (existing is None or existing == ""):
            os.environ[key] = value
            print('set', key, repr(value))
        else:
            print('skip set', key)

print('after manual', repr(os.environ.get('GROQ_API_KEY')))
