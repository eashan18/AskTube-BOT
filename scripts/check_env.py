import os
from pathlib import Path
from backend.config.settings import _load_env_file, get_settings

print('cwd', Path.cwd())
print('env path exists', Path('.env').exists())
print('.env contents first 10 lines:')
with open(Path('.env'), 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if i > 10:
            break
        print(i, repr(line.rstrip('\n')))

print('GROQ_API_KEY before load:', repr(os.environ.get('GROQ_API_KEY')))
_load_env_file()
print('GROQ_API_KEY after manual load:', repr(os.environ.get('GROQ_API_KEY')))
settings = get_settings()
print('settings.GROQ_API_KEY:', repr(settings.GROQ_API_KEY))
print('settings.BASE_URL', settings.GROQ_BASE_URL)
