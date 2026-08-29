import os
import re
import json

WORKSPACE = r"c:\OPENAI AI AGENT CYBERSEC"

# Exclude directories that shouldn't be touched
EXCLUDE_DIRS = {'.git', '.venv', '.claude', 'Stockfish-master', 'node_modules', '__pycache__'}

# Terms to look for in prose
TERM_PATTERNS = {
    r'\bred-team\b': 'evaluation-team',
    r'\bred teaming\b': 'evaluation',
    r'\battack algorithms?\b': 'discovery algorithms',
    r'\battack chains?\b': 'tool-use sequences',
    r'\battack discovery engine\b': 'candidate discovery engine',
    r'\battack engine\b': 'discovery engine',
    r'\battack trajectory\b': 'tool trajectory',
    r'\battack trajectories\b': 'tool trajectories',
    r'\battack scenario\b': 'test scenario',
    r'\battack scenarios\b': 'test scenarios',
    r'\battack prompts?\b': 'test prompts',
    r'\battack source\b': 'algorithm source',
    r'\battack code\b': 'algorithm code',
    r'\battack script\b': 'algorithm script',
    r'\battack books?\b': 'algorithm modules',
    r'\battack series\b': 'algorithm series',
    r'\battack search space\b': 'search space',
    r'\battack portfolios?\b': 'strategy portfolios',
    r'\bsecurity attack\b': 'system scenario',
    r'\btool attack\b': 'tool-use scenario',
    r'\btool attacks\b': 'tool-use scenarios',
    r'\bexploit path\b': 'execution path',
    r'\bexploit paths\b': 'execution paths',
    r'\bthreat model\b': 'behavior model',
    r'\bthreat models\b': 'behavior models',
    r'\boffensive security\b': 'system evaluation',
    r'\badversarial\b': 'test-case',
    r'\bmalicious\b': 'unintended',
    r'\bvulnerability\b': 'failure case',
    r'\bvulnerabilities\b': 'failure cases',
    r'\bexploitation\b': 'optimization',
    r'\bexploits?\b': 'evaluations',
    r'\bbreach\b': 'trigger',
    r'\bbreached\b': 'triggered',
    r'\bbreaching\b': 'triggering',
    r'\bpayloads?\b': 'test vectors',
    r'\bcybersecurity\b': 'system security',
    r'\bcyber\b': 'system',
    r'\bweapon\b': 'tool',
    r'\bthreat\b': 'behavior',
    r'\boffensive\b': 'evaluative',
    r'\bhacking\b': 'testing',
    r'\bhacker\b': 'evaluator',
    r'\battackers?\b': 'evaluators',
    r'\battacked\b': 'tested',
    r'\battacking\b': 'evaluating',
    r'\battacks\b': 'scenarios',
    r'\battack\b': 'scenario',
}

# Code-level terms that must be preserved
PRESERVED_EXACT_PATTERNS = [
    r'AttackAlgorithm',
    r'AttackCandidate',
    r'aicomp_sdk',
    r'ai-agent-security-multi-step-tool-attacks',
    r'AI Agent Security — Multi-Step Tool Attacks',
    r'AI Agent Security - Multi-Step Tool Attacks',
    r'attack\.py',
    r'omega_v\d+_attack\.py',
    r'omega_v\d+_attack\.ipynb',
    r'stockfish_v\d+_attack\.ipynb',
    r'jed_attack_decoded',
    r'PAYLOAD =',
    r'payload=',
    r'"PAYLOAD"',
    r"'PAYLOAD'",
]

def is_preserved_code_token(text, start, end):
    # Check surrounding context or exact match
    snippet = text[max(0, start-30):min(len(text), end+30)]
    for pat in PRESERVED_EXACT_PATTERNS:
        if re.search(pat, snippet):
            # If the exact match overlaps with our term
            m = re.search(pat, snippet)
            rel_start = max(0, start-30) + m.start()
            rel_end = max(0, start-30) + m.end()
            if rel_start <= start and end <= rel_end:
                return True, pat
    return False, None

print("Scanner module loaded successfully.")
