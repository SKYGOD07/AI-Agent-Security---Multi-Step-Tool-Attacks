import os
import re
import json

WORKSPACE = r"c:\OPENAI AI AGENT CYBERSEC"

EXCLUDE_DIRS = {'.git', '.venv', '.claude', 'Stockfish-master', 'node_modules', '__pycache__', 'scratch'}

REPLACEMENTS = [
    # Complex phrases first
    (r'\bRed-Team Discovery Engine\b', 'Candidate Discovery Engine', 'prose'),
    (r'\bred-team discovery engine\b', 'candidate discovery engine', 'prose'),
    (r'\bRed-Team Engine\b', 'Discovery Engine', 'prose'),
    (r'\bred-team engine\b', 'discovery engine', 'prose'),
    (r'\bred-team attack algorithms?\b', 'discovery algorithms', 'prose'),
    (r'\bred-team attack algorithm\b', 'discovery algorithm', 'prose'),
    (r'\bred-team\b', 'evaluation', 'prose'),
    (r'\bred teaming\b', 'evaluation', 'prose'),
    
    (r'\bmulti-step tool attacks\b', 'multi-step tool-use scenarios', 'prose'),
    (r'\bMulti-Step Tool Attacks\b', 'Multi-Step Tool-Use Scenarios', 'prose'),
    (r'\bsecurity attack\b', 'tool-use scenario', 'prose'),
    (r'\btool attack\b', 'tool-use scenario', 'prose'),
    (r'\btool attacks\b', 'tool-use scenarios', 'prose'),
    
    (r'\battack algorithms?\b', 'discovery algorithms', 'prose'),
    (r'\battack algorithm\b', 'discovery algorithm', 'prose'),
    (r'\battack chains?\b', 'tool-use sequences', 'prose'),
    (r'\battack chain\b', 'tool-use sequence', 'prose'),
    (r'\battack trajectory\b', 'tool trajectory', 'prose'),
    (r'\battack trajectories\b', 'tool trajectories', 'prose'),
    (r'\battack scenarios?\b', 'test scenarios', 'prose'),
    (r'\battack scenario\b', 'test scenario', 'prose'),
    (r'\battack prompts?\b', 'test prompts', 'prose'),
    (r'\battack prompt\b', 'test prompt', 'prose'),
    (r'\battack source\b', 'algorithm source', 'prose'),
    (r'\battack code\b', 'algorithm code', 'prose'),
    (r'\battack script\b', 'algorithm script', 'prose'),
    (r'\battack books?\b', 'algorithm modules', 'prose'),
    (r'\battack book\b', 'algorithm module', 'prose'),
    (r'\battack series\b', 'algorithm series', 'prose'),
    (r'\battack search space\b', 'search space', 'prose'),
    (r'\battack portfolios?\b', 'strategy portfolios', 'prose'),
    (r'\battack portfolio\b', 'strategy portfolio', 'prose'),
    (r'\battack engine\b', 'discovery engine', 'prose'),
    
    (r'\bexploit paths?\b', 'execution paths', 'prose'),
    (r'\bexploit path\b', 'execution path', 'prose'),
    (r'\bthreat models?\b', 'behavior models', 'prose'),
    (r'\bthreat model\b', 'behavior model', 'prose'),
    (r'\boffensive security\b', 'system evaluation', 'prose'),
    
    (r'\badversarial prompts?\b', 'test prompts', 'prose'),
    (r'\badversarial prompt\b', 'test prompt', 'prose'),
    (r'\badversarial\b', 'test-case', 'prose'),
    (r'\bmalicious\b', 'unintended', 'prose'),
    (r'\bvulnerabilities\b', 'failure cases', 'prose'),
    (r'\bvulnerability\b', 'failure case', 'prose'),
    (r'\bexploitation\b', 'optimization', 'prose'),
    (r'\bexploits\b', 'evaluations', 'prose'),
    (r'\bexploit\b', 'evaluate', 'prose'),
    (r'\bbreaches\b', 'triggers', 'prose'),
    (r'\bbreached\b', 'triggered', 'prose'),
    (r'\bbreaching\b', 'triggering', 'prose'),
    (r'\bbreach\b', 'trigger', 'prose'),
    (r'\bpayloads\b', 'test vectors', 'prose'),
    (r'\bpayload\b', 'test vector', 'prose'),
    (r'\bcybersecurity\b', 'system security', 'prose'),
    (r'\bcyber\b', 'system', 'prose'),
    (r'\bweapons?\b', 'tools', 'prose'),
    (r'\bthreats\b', 'behaviors', 'prose'),
    (r'\bthreat\b', 'behavior', 'prose'),
    (r'\boffensive\b', 'evaluative', 'prose'),
    (r'\bhacking\b', 'testing', 'prose'),
    (r'\bhackers\b', 'evaluators', 'prose'),
    (r'\bhacker\b', 'evaluator', 'prose'),
    (r'\battackers\b', 'evaluators', 'prose'),
    (r'\battacker\b', 'evaluator', 'prose'),
    (r'\battacked\b', 'tested', 'prose'),
    (r'\battacking\b', 'evaluating', 'prose'),
    (r'\battacks\b', 'scenarios', 'prose'),
    (r'\battack\b', 'scenario', 'prose'),
]

# Patterns that MUST BE PRESERVED when cleaning
PRESERVED_PATTERNS = [
    r'AttackAlgorithm',
    r'AttackCandidate',
    r'aicomp_sdk',
    r'AI Agent Security — Multi-Step Tool Attacks',
    r'AI Agent Security - Multi-Step Tool Attacks',
    r'ai-agent-security-multi-step-tool-attacks',
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

print("Batch cleaner helper created.")
