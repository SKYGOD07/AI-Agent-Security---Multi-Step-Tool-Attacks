import os
import re
import json

WORKSPACE = r"c:\OPENAI AI AGENT CYBERSEC"
EXCLUDE_DIRS = {'.git', '.venv', '.claude', 'Stockfish-master', 'node_modules', '__pycache__', 'scratch'}

REPLACEMENTS = [
    (re.compile(r'\bRed-Team Discovery Engine\b'), 'Candidate Discovery Engine'),
    (re.compile(r'\bred-team discovery engine\b'), 'candidate discovery engine'),
    (re.compile(r'\bRed-Team Engine\b'), 'Discovery Engine'),
    (re.compile(r'\bred-team engine\b'), 'discovery engine'),
    (re.compile(r'\bred-team attack algorithms?\b', re.I), 'discovery algorithms'),
    (re.compile(r'\bred-team attack algorithm\b', re.I), 'discovery algorithm'),
    (re.compile(r'\bred-team attack\b', re.I), 'evaluation scenario'),
    (re.compile(r'\bred-team\b', re.I), 'evaluation'),
    (re.compile(r'\bred teaming\b', re.I), 'evaluation'),
    
    (re.compile(r'\bmulti-step tool attacks\b'), 'multi-step tool-use scenarios'),
    (re.compile(r'\bMulti-Step Tool Attacks\b'), 'Multi-Step Tool-Use Scenarios'),
    (re.compile(r'\bsecurity attack\b', re.I), 'tool-use scenario'),
    (re.compile(r'\btool attack\b', re.I), 'tool-use scenario'),
    (re.compile(r'\btool attacks\b', re.I), 'tool-use scenarios'),
    
    (re.compile(r'\battack algorithms?\b', re.I), 'discovery algorithms'),
    (re.compile(r'\battack algorithm\b', re.I), 'discovery algorithm'),
    (re.compile(r'\battack chains?\b', re.I), 'tool-use sequences'),
    (re.compile(r'\battack chain\b', re.I), 'tool-use sequence'),
    (re.compile(r'\battack trajectory\b', re.I), 'tool trajectory'),
    (re.compile(r'\battack trajectories\b', re.I), 'tool trajectories'),
    (re.compile(r'\battack scenarios?\b', re.I), 'test scenarios'),
    (re.compile(r'\battack scenario\b', re.I), 'test scenario'),
    (re.compile(r'\battack prompts?\b', re.I), 'test prompts'),
    (re.compile(r'\battack prompt\b', re.I), 'test prompt'),
    (re.compile(r'\battack source\b', re.I), 'algorithm source'),
    (re.compile(r'\battack code\b', re.I), 'algorithm code'),
    (re.compile(r'\battack script\b', re.I), 'algorithm script'),
    (re.compile(r'\battack books?\b', re.I), 'algorithm modules'),
    (re.compile(r'\battack book\b', re.I), 'algorithm module'),
    (re.compile(r'\battack series\b', re.I), 'algorithm series'),
    (re.compile(r'\battack search space\b', re.I), 'search space'),
    (re.compile(r'\battack portfolios?\b', re.I), 'strategy portfolios'),
    (re.compile(r'\battack portfolio\b', re.I), 'strategy portfolio'),
    (re.compile(r'\battack engine\b', re.I), 'discovery engine'),
    
    (re.compile(r'\bexploit paths?\b', re.I), 'execution paths'),
    (re.compile(r'\bexploit path\b', re.I), 'execution path'),
    (re.compile(r'\bthreat models?\b', re.I), 'behavior models'),
    (re.compile(r'\bthreat model\b', re.I), 'behavior model'),
    (re.compile(r'\boffensive security\b', re.I), 'system evaluation'),
    
    (re.compile(r'\badversarial prompts?\b', re.I), 'test prompts'),
    (re.compile(r'\badversarial prompt\b', re.I), 'test prompt'),
    (re.compile(r'\badversarial\b', re.I), 'test-case'),
    (re.compile(r'\bmalicious\b', re.I), 'unintended'),
    (re.compile(r'\bvulnerabilities\b', re.I), 'failure cases'),
    (re.compile(r'\bvulnerability\b', re.I), 'failure case'),
    (re.compile(r'\bexploitation\b', re.I), 'optimization'),
    (re.compile(r'\bexploits\b', re.I), 'evaluations'),
    (re.compile(r'\bexploit\b', re.I), 'evaluate'),
    (re.compile(r'\bbreaches\b', re.I), 'triggers'),
    (re.compile(r'\bbreached\b', re.I), 'triggered'),
    (re.compile(r'\bbreaching\b', re.I), 'triggering'),
    (re.compile(r'\bbreach\b', re.I), 'trigger'),
    (re.compile(r'\bpayloads\b', re.I), 'test vectors'),
    (re.compile(r'\bpayload\b', re.I), 'test vector'),
    (re.compile(r'\bcybersecurity\b', re.I), 'system security'),
    (re.compile(r'\bcyber\b', re.I), 'system'),
    (re.compile(r'\bweapons?\b', re.I), 'tools'),
    (re.compile(r'\bthreats\b', re.I), 'behaviors'),
    (re.compile(r'\bthreat\b', re.I), 'behavior'),
    (re.compile(r'\boffensive\b', re.I), 'evaluative'),
    (re.compile(r'\bhacking\b', re.I), 'testing'),
    (re.compile(r'\bhackers\b', re.I), 'evaluators'),
    (re.compile(r'\bhacker\b', re.I), 'evaluator'),
    (re.compile(r'\battackers\b', re.I), 'evaluators'),
    (re.compile(r'\battacker\b', re.I), 'evaluator'),
    (re.compile(r'\battacked\b', re.I), 'tested'),
    (re.compile(r'\battacking\b', re.I), 'evaluating'),
    (re.compile(r'\battacks\b', re.I), 'scenarios'),
    (re.compile(r'\battack\b', re.I), 'scenario'),
]

PRESERVE_SUBSTRINGS = [
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

modified_files = []

for root, dirs, files in os.walk(WORKSPACE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.md', '.txt']:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, WORKSPACE)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.splitlines(keepends=True)
                new_lines = []
                file_mods = 0
                
                for line in lines:
                    has_preserved = any(p in line for p in PRESERVE_SUBSTRINGS)
                    if re.search(r'omega_v\d+_attack\.(py|ipynb)', line) or re.search(r'stockfish_v\d+_attack\.(py|ipynb)', line):
                        has_preserved = True
                    
                    if has_preserved:
                        new_lines.append(line)
                    else:
                        orig = line
                        for pat, repl in REPLACEMENTS:
                            line = pat.sub(repl, line)
                        if line != orig:
                            file_mods += 1
                        new_lines.append(line)
                
                new_content = "".join(new_lines)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified_files.append((rel_path, file_mods))
            except Exception as e:
                print(f"Error processing {rel_path}: {e}")

print(f"Cleanup complete. Total modified markdown/text files: {len(modified_files)}")
print(json.dumps(modified_files[:20], indent=2))
