import os
import re
import json

WORKSPACE = r"c:\OPENAI AI AGENT CYBERSEC"
EXCLUDE_DIRS = {'.git', '.venv', '.claude', 'Stockfish-master', 'node_modules', '__pycache__', 'scratch'}

TERMS = [
    "attack", "attacker", "attacking", "exploit", "exploitation", "exploit path",
    "malicious", "adversarial", "red-team", "red teaming", "cybersecurity", "cyber",
    "security attack", "tool attack", "attack algorithm", "attack chain",
    "attack trajectory", "vulnerability", "compromise", "breach", "payload",
    "weapon", "threat", "threat model", "offensive", "offensive security",
    "hacking", "hacker"
]

PRESERVED_EXACT = [
    "AttackAlgorithm",
    "AttackCandidate",
    "aicomp_sdk",
    "AI Agent Security — Multi-Step Tool Attacks",
    "AI Agent Security - Multi-Step Tool Attacks",
    "ai-agent-security-multi-step-tool-attacks",
    "attack.py",
    "jed_attack_decoded",
    "PAYLOAD =",
    "payload=",
    '"PAYLOAD"',
    "'PAYLOAD'",
    "track redteam",
    "track=redteam",
    "track='redteam'",
    'track="redteam"',
    "--track redteam"
]

pattern = re.compile(r'\b(' + '|'.join([re.escape(t) for t in TERMS]) + r')\b', re.IGNORECASE)

preserved_occurrences = []
unpreserved_occurrences = []

for root, dirs, files in os.walk(WORKSPACE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        filepath = os.path.join(root, file)
        rel_path = os.path.relpath(filepath, WORKSPACE)
        ext = os.path.splitext(file)[1].lower()
        
        if ext in ['.md', '.txt', '.py', '.ipynb']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                lines = content.splitlines()
                for line_idx, line in enumerate(lines, 1):
                    matches = list(pattern.finditer(line))
                    if matches:
                        is_preserved = any(p in line for p in PRESERVED_EXACT) or bool(re.search(r'omega_v\d+_attack\.(py|ipynb)', line)) or bool(re.search(r'stockfish_v\d+_attack\.(py|ipynb)', line))
                        
                        for m in matches:
                            item = {
                                "file": rel_path,
                                "line": line_idx,
                                "term": m.group(0),
                                "context": line.strip()[:100]
                            }
                            if is_preserved:
                                item["reason"] = "Required by Python class name, SDK API, official dataset/competition title, or code filename"
                                preserved_occurrences.append(item)
                            else:
                                unpreserved_occurrences.append(item)
            except Exception as e:
                pass

report = {
    "total_preserved_occurrences": len(preserved_occurrences),
    "total_unpreserved_occurrences": len(unpreserved_occurrences),
    "sample_preserved": preserved_occurrences[:15],
    "sample_unpreserved": unpreserved_occurrences[:15]
}

print(json.dumps(report, indent=2))
