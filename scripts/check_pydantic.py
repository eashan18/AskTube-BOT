import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

for name in ['pydantic', 'pydantic_settings']:
    try:
        mod = __import__(name)
        print(name, 'loaded', getattr(mod, '__file__', 'builtin'), 'version', getattr(mod, '__version__', 'unknown'))
    except Exception as e:
        print(name, 'failed', type(e).__name__, e)

import backend.config.settings as settings_mod
print('Backend settings module', settings_mod.__file__)
print('BaseSettings type', settings_mod.BaseSettings)
print('Has model_config?', hasattr(settings_mod.BaseSettings, 'model_config'))
print('Settings type', settings_mod.Settings)
try:
    env_key = os.environ.get('GROQ_API_KEY')
    print('GROQ_API_KEY env before', repr(env_key))
    settings_mod._load_env_file()
    print('GROQ_API_KEY env after load', repr(os.environ.get('GROQ_API_KEY')))
    s = settings_mod.Settings()
    print('Settings.GROQ_API_KEY', repr(s.GROQ_API_KEY))
except Exception as e:
    import traceback
    traceback.print_exc()
