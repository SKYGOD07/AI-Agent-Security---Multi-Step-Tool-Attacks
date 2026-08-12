"""Build OMEGA v8 notebook: omega_v8_attack.ipynb"""

import base64
import json
from pathlib import Path

DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DIR.parents[2]

attack_src = (DIR / "omega_v8_attack.py").read_text(encoding="utf-8")
attack_b64 = base64.b64encode(attack_src.encode("utf-8")).decode("ascii")

nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega8-setup",
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
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega8-attack",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import base64\n",
                f'ATTACK_B64 = "{attack_b64}"\n',
                "src = base64.b64decode(ATTACK_B64).decode('utf-8')\n",
                "with open('/kaggle/working/attack.py', 'w') as fh:\n",
                "    fh.write(src)\n",
                "print('attack.py written:', len(src), 'chars')\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "omega8-submit",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import os, sys, glob, csv\n",
                'COMP = "ai-agent-security-multi-step-tool-attacks"\n',
                'IS_RERUN = os.getenv("KAGGLE_IS_COMPETITION_RERUN")\n',
                "\n",
                'for p in [f"/kaggle/input/{COMP}", *glob.glob("/kaggle/input/*")]:\n',
                '    if os.path.isdir(os.path.join(p, "kaggle_evaluation")) and p not in sys.path:\n',
                "        sys.path.insert(0, p)\n",
                "        break\n",
                "\n",
                "from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import JEDAttackInferenceServer\n",
                "\n",
                "server = JEDAttackInferenceServer()\n",
                "if IS_RERUN:\n",
                "    server.serve()\n",
                "else:\n",
                '    with open("/kaggle/working/submission.csv", "w", newline="") as fh:\n',
                '        w = csv.writer(fh)\n',
                '        w.writerow(["Id", "Score"])\n',
                '        w.writerows([["gpt_oss_public", 0.0], ["gpt_oss_private", 0.0],\n',
                '                      ["gemma_public", 0.0], ["gemma_private", 0.0]])\n',
                '    print("placeholder submission.csv written")\n',
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

output_path = PROJECT_ROOT / "our_work" / "notebooks" / "omega_v8_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ===== Validation =====
print("=" * 60)
print("OMEGA v8 (Clean Recovery) Notebook Validation")
print("=" * 60)

with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

assert len(verify["cells"]) == 3
print(f"[OK] Cell count: {len(verify['cells'])}")

b64_line = [l for l in verify["cells"][1]["source"] if "ATTACK_B64" in l and "=" in l][0]
decoded = base64.b64decode(b64_line.split('"')[1]).decode("utf-8")

compile(decoded, "attack.py", "exec")
print("[OK] Decoded attack.py compiles without syntax errors")

# Core checks
for pattern, desc in [
    ("AttackAlgorithmBase", "Inherits from AttackAlgorithmBase"),
    ("AttackCandidate", "Uses AttackCandidate"),
    ("AttackRunConfig", "Uses AttackRunConfig"),
    ("class AttackAlgorithm", "Defines AttackAlgorithm class"),
    ("def run(", "Defines run() method"),
    ("SECRET_MARKER", "Uses SECRET_MARKER payload"),
    ("http.post", "Targeting http.post"),
    ("<|end|><|start|>assistant<|channel|>analysis<|message|><|end|>", "Harmony frame template"),
]:
    assert pattern in decoded, f"FAIL: {desc}"
    print(f"[OK] {desc}")

# v8 = exact v5 verification
print(f"\n--- OMEGA v8 = v5 Exact Match Checks ---")
for pattern, desc in [
    ("REPLAY_SAFE_FRAC = 0.99", "v5 proven REPLAY_SAFE_FRAC = 0.99"),
    ("SPLIT_CLASSIFY_N = 3", "v5 proven SPLIT_CLASSIFY_N = 3"),
    ("SLOWEST0 = 25.0", "v5 proven SLOWEST0 = 25"),
    ("SLOWEST_MULT = 1.20", "v5 proven SLOWEST_MULT = 1.20"),
    ("max_tool_hops=1", "Warm-up at hops=1 (NOT hops=2!)"),
    ("warmup_fired", "Warm-up candidate harvesting"),
]:
    assert pattern in decoded, f"FAIL: {desc}"
    print(f"[OK] {desc}")

# Verify NO v7 multi-predicate artifacts
print(f"\n--- v7 Regression Safeguards ---")
# Strip docstrings and comments, then check no multi-predicate CODE exists
import re
code_only = re.sub(r'"""[\s\S]*?"""', '', decoded)
code_only = re.sub(r"'''[\s\S]*?'''", '', code_only)
code_only = "\n".join(l for l in code_only.split("\n") if not l.strip().startswith("#"))
assert "MULTI_TEMPLATE" not in code_only
print("[OK] No MULTI_TEMPLATE variable (v7 regression cause)")
assert "fs.delete" not in code_only
print("[OK] No fs.delete in code (v7 regression cause)")
assert "_fired_multi" not in code_only
print("[OK] No _fired_multi method (v7 regression cause)")
assert "max_tool_hops=2" not in code_only
print("[OK] No hops=2 warm-up (v7 regression cause)")
assert "multi_ok" not in code_only
print("[OK] No multi_ok flag (v7 regression cause)")

# Double-counting bug check
assert "replay_cost += (time.monotonic() - run_start)" not in decoded
print("[OK] Double-counting bug remains FIXED")

print(f"\n[INFO] attack.py: {len(decoded)} chars, {len(decoded.splitlines())} lines")
print(f"[INFO] Notebook: {output_path}")
print("=" * 60)
print("ALL VALIDATIONS PASSED -- OMEGA v8 notebook is ready!")
print("=" * 60)
