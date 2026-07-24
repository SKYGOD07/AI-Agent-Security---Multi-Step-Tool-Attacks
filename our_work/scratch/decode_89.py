import json
import base64
with open(r'c:\OPENAI AI AGENT CYBERSEC\zOthers works\ai-agent-security-solution.ipynb', 'r') as f:
    nb = json.load(f)
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if 'ATTACK_PY_B64 = "' in src:
            b64 = src.split('ATTACK_PY_B64 = "')[1].split('"')[0]
            with open(r'c:\OPENAI AI AGENT CYBERSEC\our_work\scratch\89_055_decoded.py', 'w', encoding='utf-8') as out:
                out.write(base64.b64decode(b64).decode('utf-8'))
            print('Decoded to scratch/89_055_decoded.py')
            break
