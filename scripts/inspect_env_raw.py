from pathlib import Path
p = Path('.env')
print('path', p.resolve())
print('exists', p.exists())
with p.open('rb') as f:
    lines = f.readlines()
for idx, line in enumerate(lines, start=1):
    if b'GROQ_API_KEY' in line or idx in range(20, 27):
        print(idx, repr(line), line.decode('utf-8', errors='replace'))
print('----')
if any(b'GROQ_API_KEY=' in line for line in lines):
    print('found line with key')
