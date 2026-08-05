"""Build OMEGA v2 notebook: omega_v2_attack.ipynb

Reads omega_v2_attack.py, base64-encodes it, and builds a 3-cell Kaggle
competition notebook with complete validation.
"""

import base64
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DIR.parents[1]  # our_work/versions/v32 -> root

# Read attack source
attack_src = (DIR / "omega_v2_attack.py").read_text(encoding="utf-8")
attack_b64 = base64.b64encode(attack_src.encode("utf-8")).decode("ascii")

nb = {
    "cells": [
        # Cell 1: Setup
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega2-setup",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import sys, glob\n",
                "from pathlib import Path\n",
                "sys.argv = [sys.argv[0]]\n",
                "for c in glob.glob('/kaggle/input/**/kaggle_evaluation', recursive=True):\n",
                "    p = str(Path(c).parent)\n",
                "    if p not in sys.path:\n",
                "        sys.path.insert(0, p)\n",
                "    print('Dataset root:', p)\n",
                "    break\n",
                "print('Setup complete')\n",
            ],
        },
        # Cell 2: Write attack.py
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega2-attack",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import base64\n",
                f"ATTACK_B64 = \"{attack_b64}\"\n",
                "src = base64.b64decode(ATTACK_B64).decode('utf-8')\n",
                "with open('/kaggle/working/attack.py', 'w') as fh:\n",
                "    fh.write(src)\n",
                "print('attack.py written:', len(src), 'chars')\n",
            ],
        },
        # Cell 3: Submission & Inference Server
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega2-submit",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import os, sys, glob, csv\n",
                "COMP = \"ai-agent-security-multi-step-tool-attacks\"\n",
                "IS_RERUN = os.getenv(\"KAGGLE_IS_COMPETITION_RERUN\")\n",
                "\n",
                "for p in [f\"/kaggle/input/{COMP}\", *glob.glob(\"/kaggle/input/*\")]:\n",
                "    if os.path.isdir(os.path.join(p, \"kaggle_evaluation\")) and p not in sys.path:\n",
                "        sys.path.insert(0, p)\n",
                "        break\n",
                "\n",
                "from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import JEDAttackInferenceServer\n",
                "\n",
                "server = JEDAttackInferenceServer()\n",
                "if IS_RERUN:\n",
                "    server.serve()\n",
                "else:\n",
                "    with open(\"/kaggle/working/submission.csv\", \"w\", newline=\"\") as fh:\n",
                "        w = csv.writer(fh)\n",
                "        w.writerow([\"Id\", \"Score\"])\n",
                "        w.writerows([[\"gpt_oss_public\", 0.0], [\"gpt_oss_private\", 0.0],\n",
                "                      [\"gemma_public\", 0.0], [\"gemma_private\", 0.0]])\n",
                "    print(\"placeholder submission.csv written\")\n",
            ],
        },
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.12.13",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

output_path = PROJECT_ROOT / "our_work" / "notebooks" / "omega_v2_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ===== Validation =====
print("=" * 60)
print("OMEGA v2 Notebook Validation")
print("=" * 60)

with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])
assert cell_count == 3
print(f"[OK] Cell count: {cell_count}")

b64_line = [l for l in verify["cells"][1]["source"] if "ATTACK_B64" in l and "=" in l][0]
b64_val = b64_line.split('"')[1]
decoded = base64.b64decode(b64_val).decode("utf-8")

# Validate python compilation
compile(decoded, "attack.py", "exec")
print("[OK] Decoded attack.py compiles without syntax errors")

checks = [
    ("AttackAlgorithmBase", "Inherits from AttackAlgorithmBase"),
    ("AttackCandidate", "Uses AttackCandidate"),
    ("AttackRunConfig", "Uses AttackRunConfig"),
    ("class AttackAlgorithm", "Defines AttackAlgorithm class"),
    ("def run(", "Defines run() method"),
    ("SECRET_MARKER", "Uses SECRET_MARKER payload"),
    ("http.post", "Targeting http.post"),
    ("FRAME_TEMPLATE", "Uses Harmony frame template for gpt_oss"),
    ("_forge_plan_msg", "Uses token-forged multi-post for gpt_oss"),
    ("REPLAY_SAFE_FRAC = 0.965", "Uses conservative replay safety fraction"),
]

for pattern, desc in checks:
    assert pattern in decoded, f"FAIL: {desc} - missing '{pattern}'"
    print(f"[OK] {desc}")

print(f"\n[INFO] attack.py size: {len(decoded)} chars, {len(decoded.splitlines())} lines")
print(f"[INFO] Notebook path: {output_path}")

print("=" * 60)
print("ALL VALIDATIONS PASSED — OMEGA v2 notebook is ready!")
print("=" * 60)
