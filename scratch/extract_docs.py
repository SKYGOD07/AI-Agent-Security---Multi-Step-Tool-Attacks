import json
import base64
import glob
import re

for path in sorted(glob.glob(r'c:\OPENAI AI AGENT CYBERSEC\our_work\notebooks\omega_v*.ipynb')):
    m = re.search(r'v(\d+)', path)
    if m:
        v_num = int(m.group(1))
        if v_num >= 29:
            with open(path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
            for cell in nb['cells']:
                src = ''.join(cell['source'])
                if 'ATTACK_B64' in src:
                    match = re.search(r'ATTACK_B64\s*=\s*"([^"]+)"', src)
                    if match:
                        b64_str = match.group(1)
                        code = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
                        parts = code.split('"""')
                        doc = parts[1] if len(parts) > 1 else code[:300]
                        print(f"=== v{v_num} ===")
                        print(doc.strip()[:400])
                        print("-" * 50)
