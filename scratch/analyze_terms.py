import os
import re
import json

TARGET_DIR = r"c:\OPENAI AI AGENT CYBERSEC"

TERMS = [
    "attack", "attacker", "attacking", "exploit", "exploitation", "exploit path",
    "malicious", "adversarial", "red-team", "red teaming", "cybersecurity", "cyber",
    "security attack", "tool attack", "attack algorithm", "attack chain",
    "attack trajectory", "vulnerability", "compromise", "breach", "payload",
    "weapon", "threat", "threat model", "offensive", "offensive security",
    "hacking", "hacker"
]

pattern = re.compile(r'\b(' + '|'.join([re.escape(t) for t in TERMS]) + r')\b', re.IGNORECASE)

results = []

for root, dirs, files in os.walk(TARGET_DIR):
    # Ignore git and pycache
    if '.git' in root or '__pycache__' in root or '.claude' in root:
        continue
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        filepath = os.path.join(root, file)
        rel_path = os.path.relpath(filepath, TARGET_DIR)
        
        if ext in ['.md', '.txt', '.py', '.ipynb', '.json']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                matches = list(pattern.finditer(content))
                if matches:
                    results.append({
                        "file": rel_path,
                        "ext": ext,
                        "count": len(matches),
                        "terms_found": list(set([m.group(0).lower() for m in matches]))
                    })
            except Exception as e:
                pass

print(f"Total files with target terms: {len(results)}")
print(json.dumps(results[:30], indent=2))
