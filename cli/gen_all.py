import subprocess
import os
import json

_HERE   = os.path.dirname(os.path.abspath(__file__))
_ROOT   = os.path.dirname(_HERE)
_GEN_PY = os.path.join(_HERE, 'gen.py')
_OPTS   = os.path.join(_ROOT, 'default_opts.json')
_OUT    = os.path.join(_ROOT, 'codici')

scope_id = input("Enter ScopeID (hex): ").strip()

with open(_OPTS, 'r') as f:
    options = json.load(f)

with open(_OUT, 'w') as out_f:
    for item in options:
        code = item["code"]
        flags, mask = code.split('-')
        result = subprocess.run(
            ['python', _GEN_PY, scope_id, flags, mask],
            capture_output=True, text=True
        )
        out_f.write(result.stdout.strip() + '\t' + item["key"] + '\t' + item["description"] + '\n')

print(f"Codici generati e salvati in: {_OUT}")