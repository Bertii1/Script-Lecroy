import subprocess
import os
import json

# Ask for ScopeID
scope_id = input("Enter ScopeID (hex): ").strip()

# Read opzioni.json
with open('opzioni.json', 'r') as f:
    options = json.load(f)

# Open codici for writing (overwrite)
with open('codici', 'w') as out_f:
    # For each option
    for item in options:
        code = item["code"]
        flags, mask = code.split('-')
        # Run gen.py
        result = subprocess.run(['python', 'gen.py', scope_id, flags, mask], capture_output=True, text=True, cwd=os.getcwd())
        key = result.stdout.strip()
        # Write to codici
        out_f.write(key + '\t' + item["key"] + '\t' + item["description"] + '\n')

print("Codici generated and saved to codici.")