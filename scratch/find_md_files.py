import os
import re
import json

WORKSPACE = r"c:\OPENAI AI AGENT CYBERSEC"

# Exclude directories
EXCLUDE_DIRS = {'.git', '.venv', '.claude', 'Stockfish-master', 'node_modules', '__pycache__', 'scratch'}

# List of markdown & text files in the project to clean
MD_TXT_FILES = []
for root, dirs, files in os.walk(WORKSPACE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.md', '.txt']:
            MD_TXT_FILES.append(os.path.join(root, file))

print(f"Found {len(MD_TXT_FILES)} markdown/text files.")
