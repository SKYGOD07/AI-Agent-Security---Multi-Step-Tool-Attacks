"""Build v27 notebook: v69-architecture attack in 3-cell scaffold."""

import json

# ---- Load the decoded attack.py ----
with open("our_work/jed_attack_decoded_v27.py", "r", encoding="utf-8") as f:
    attack_py = f.read()

# ---- Build the notebook (matches v69's proven 3-cell structure) ----
nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": "47748b87",
            "metadata": {"tags": []},
            "source": [
                "### 1 \u00b7 Write `attack.py`  (set TEMPLATE / N_CANDIDATES / MSGS_PER_CANDIDATE here)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "4fa6dbcb",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [],
        },
        {
            "cell_type": "markdown",
            "id": "02be94bd",
            "metadata": {"tags": []},
            "source": [
                "### 2 \u00b7 Serve \u2014 commit run writes a local submission.csv; rerun is scored\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "f6b4856d",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [
                "import os, sys, glob\n",
                "COMP = \"ai-agent-security-multi-step-tool-attacks\"\n",
                "IS_RERUN = os.getenv(\"KAGGLE_IS_COMPETITION_RERUN\")\n",
                "\n",
                "for p in [f\"/kaggle/input/{COMP}\", *glob.glob(\"/kaggle/input/*\")]:\n",
                "    if os.path.isdir(os.path.join(p, \"kaggle_evaluation\")) and p not in sys.path:\n",
                "        sys.path.insert(0, p)\n",
                "        break\n",
                "\n",
                "from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import (\n",
                "    JEDAttackInferenceServer,\n",
                ")\n",
                "\n",
                "server = JEDAttackInferenceServer()\n",
                "if IS_RERUN:\n",
                "    server.serve()   # scored rerun: gateway replays vs gpt_oss/gemma, writes the REAL submission.csv\n",
                "else:\n",
                "    import csv\n",
                "    with open(\"submission.csv\", \"w\", newline=\"\") as fh:\n",
                "        w = csv.writer(fh); w.writerow([\"Id\", \"Score\"]); w.writerows([[\"gpt_oss_public\", 0.0], [\"gpt_oss_private\", 0.0], [\"gemma_public\", 0.0], [\"gemma_private\", 0.0]])\n",
                "    print(\"placeholder submission.csv written. Set Accelerator = GPU T4 x2, then Submit.\")\n",
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

# ---- Format attack.py as %%writefile cell source ----
writefile_header = "%%writefile /kaggle/working/attack.py\n"
lines = attack_py.split("\n")
cell_source = [writefile_header]
for i, line in enumerate(lines):
    if i < len(lines) - 1:
        cell_source.append(line + "\n")
    elif line:
        cell_source.append(line)

nb["cells"][1]["source"] = cell_source

# ---- Write the notebook ----
output_path = "our_work/notebooks/stockfish_v27_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ---- Validate ----
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])
code = "".join(verify["cells"][1]["source"])
serve = "".join(verify["cells"][3]["source"])

assert cell_count == 4, f"Expected 4 cells (2 md + 2 code), got {cell_count}"
assert "%%writefile /kaggle/working/attack.py" in code
assert "MARGIN_S = 42.0" in code, "MARGIN_S must be 42.0"
assert "FILL_BUDGET_FRAC = 0.97" in code, "FILL_BUDGET_FRAC must be 0.97"
assert "MARGIN_FLOOR_MIN = 3.0" in code, "MARGIN_FLOOR_MIN must be 3.0"
assert "SPLIT_CLASSIFY_N = 6" in code, "SPLIT_CLASSIFY_N must be 6"
assert "REPLAY_SAFE_FRAC = 0.97" in code, "REPLAY_SAFE_FRAC must be 0.97"
assert "SPLIT_BY_LATENCY = True" in code, "SPLIT_BY_LATENCY must be True"
assert "BURST_K = 1" in code, "BURST_K must be 1"
assert "SLOW_MULTIPOST_N = 1" in code, "SLOW_MULTIPOST_N must be 1"
assert "SECRET_MARKER" in code
assert "FRAME_TEMPLATE" in code
assert "class AttackAlgorithm" in code
assert "def run(" in code
assert "def _fill(" in code
assert "def _fired(" in code
assert "_adaptive_margin" in code
assert "_replay_stop" in code
assert "JEDAttackInferenceServer" in serve
assert "KAGGLE_IS_COMPETITION_RERUN" in serve
assert "gpt_oss_public" in serve
assert "gemma_private" in serve

print("v27 notebook created and validated!")
print(f"  Path: {output_path}")
print(f"  Cells: {cell_count}")
print(f"  attack.py: {len(code)} chars")
print("  Architecture: v69/ea-b (88.2 scorer)")
print("  MARGIN_S = 42.0 OK (tightened from v69's 47)")
print("  FILL_BUDGET_FRAC = 0.97 OK (tightened from 0.95)")
print("  MARGIN_FLOOR_MIN = 3.0 OK (tightened from 4.0)")
print("  SPLIT_BY_LATENCY = True OK")
print("  REPLAY_SAFE_SIZING = True OK")
print("  REPLAY_SAFE_FRAC = 0.97 OK")
print("  BURST_K = 1, SLOW_MULTIPOST_N = 1 OK (single-post)")
print("  Id,Score placeholder OK")
