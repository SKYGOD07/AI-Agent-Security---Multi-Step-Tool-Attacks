import json
import base64

with open('our_work/notebooks/omega_v13_attack.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for line in nb['cells'][1]['source']:
    if 'ATTACK_B64 = ' in line:
        b64 = line.split('"')[1]
        decoded = base64.b64decode(b64).decode('utf-8')
        print(decoded)
        with open('scratch/v13_decoded.py', 'w', encoding='utf-8') as out:
            out.write(decoded)
