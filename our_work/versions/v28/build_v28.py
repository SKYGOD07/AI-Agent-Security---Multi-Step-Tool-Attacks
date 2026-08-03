"""Build v28 notebook: v69 arch + jedforce-1 defensive patterns."""

import json

# ---- Load the decoded attack.py ----
with open("our_work/jed_attack_decoded_v28.py", "r", encoding="utf-8") as f:
    attack_py = f.read()

# ---- Build notebook using jedforce-1's proven 3-cell structure ----
# Cell 0: setup + sys.path (from jedforce-1)
# Cell 1: write attack.py via base64 (from jedforce-1 — avoids any encoding issues)
# Cell 2: placeholder + serve (from jedforce-1 — ALWAYS serves, no IS_RERUN gate)
import base64
attack_b64 = base64.b64encode(attack_py.encode("utf-8")).decode("ascii")

nb = {
    "cells": [
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "060490e4",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import sys, os, base64, glob\n",
                "from pathlib import Path\n",
                "sys.argv = [sys.argv[0]]\n",
                "for candidate in glob.glob('/kaggle/input/**/kaggle_evaluation', recursive=True):\n",
                "    dataset_root = str(Path(candidate).parent)\n",
                "    if dataset_root not in sys.path:\n",
                "        sys.path.insert(0, dataset_root)\n",
                "    print(f'Dataset root: {dataset_root}')\n",
                "    break\n",
                "print('Setup complete')\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "e168117f",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import base64\n",
                f"ATTACK_PY_B64 = \"{attack_b64}\"\n",
                "attack_bytes = base64.b64decode(ATTACK_PY_B64)\n",
                "with open('/kaggle/working/attack.py','wb') as f:\n",
                "    f.write(attack_bytes)\n",
                "print(f'attack.py written: {len(attack_bytes)} bytes')\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "cc8e5c4c",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "placeholder = 'Id,Score\\ngpt_oss_public,0.0\\ngpt_oss_private,0.0\\ngemma_public,0.0\\ngemma_private,0.0\\n'\n",
                "(Path('/kaggle/working') / 'submission.csv').write_text(placeholder)\n",
                "print('submission.csv placeholder written')\n",
                "from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import JEDAttackInferenceServer\n",
                "JEDAttackInferenceServer().serve()\n",
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

# ---- Write ----
output_path = "our_work/notebooks/stockfish_v28_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ---- Validate ----
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])

# Decode the attack.py from the notebook to verify contents
b64_line = [l for l in verify["cells"][1]["source"] if "ATTACK_PY_B64" in l and "=" in l][0]
b64_val = b64_line.split('"')[1]
decoded = base64.b64decode(b64_val).decode("utf-8")

serve = "".join(verify["cells"][2]["source"])

assert cell_count == 3, f"Expected 3 cells, got {cell_count}"

# Attack.py content checks
assert "MARGIN_S = 44.0" in decoded, f"MARGIN_S must be 44.0"
assert "FILL_BUDGET_FRAC = 0.96" in decoded, f"FILL_BUDGET_FRAC must be 0.96"
assert "MARGIN_FLOOR_MIN = 3.5" in decoded, f"MARGIN_FLOOR_MIN must be 3.5"
assert "SPLIT_CLASSIFY_N = 7" in decoded, f"SPLIT_CLASSIFY_N must be 7"
assert "REPLAY_SAFE_FRAC = 0.97" in decoded, f"REPLAY_SAFE_FRAC must be 0.97"
assert "SPLIT_BY_LATENCY = True" in decoded
assert "BURST_K = 1" in decoded
assert "SLOW_MULTIPOST_N = 1" in decoded
assert "SECRET_MARKER" in decoded
assert "FRAME_TEMPLATE" in decoded
assert "class AttackAlgorithm" in decoded
assert "def run(" in decoded
assert "def _fill(" in decoded
assert "def _fired(" in decoded
assert "_adaptive_margin" in decoded
assert "_replay_stop" in decoded
assert "_manual_exfil" in decoded

# Defensive patterns checks
assert "try:" in decoded and "except Exception:" in decoded, "Need defensive imports"
assert "def __init__" in decoded, "Need defensive __init__"
assert "hasattr(self, \"config\")" in decoded, "Need config safety check"

# Serve cell checks
assert "JEDAttackInferenceServer" in serve
assert "submission.csv" in serve
assert "gpt_oss_public" in serve
assert "gemma_private" in serve
assert "serve()" in serve

# Verify NO IS_RERUN gate (jedforce-1 pattern: always serve)
assert "IS_RERUN" not in serve, "jedforce-1 pattern: always serve, no IS_RERUN"

print("v28 notebook created and validated!")
print(f"  Path: {output_path}")
print(f"  Cells: {cell_count}")
print(f"  attack.py: {len(decoded)} chars (base64 encoded)")
print()
print("  === FIXES from v27 ===")
print("  [FIX] Defensive try/except SDK imports (jedforce-1 pattern)")
print("  [FIX] Defensive __init__ with config safety (jedforce-1 pattern)")
print("  [FIX] Base64 attack.py encoding (jedforce-1 pattern)")
print("  [FIX] Always-serve pattern, no IS_RERUN gate (jedforce-1 pattern)")
print("  [FIX] _manual_exfil fallback when eval_predicates unavailable")
print()
print("  === TUNING (moderate, not aggressive) ===")
print("  MARGIN_S = 44.0 (v69=47, v27=42)")
print("  FILL_BUDGET_FRAC = 0.96 (v69=0.95, v27=0.97)")
print("  MARGIN_FLOOR_MIN = 3.5 (v69=4.0, v27=3.0)")
print("  SPLIT_CLASSIFY_N = 7 (v69=8, v27=6)")
print("  REPLAY_SAFE_FRAC = 0.97 (same as v69)")
print("  BURST_K = 1, SLOW_MULTIPOST_N = 1 (single-post, safe)")
