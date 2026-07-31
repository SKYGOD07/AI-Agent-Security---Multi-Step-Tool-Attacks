"""Build v26 notebook: Replay-recalibrated dual-URL attack in v16 notebook scaffold."""

import json

# ---- Load the decoded attack.py ----
with open("our_work/jed_attack_decoded_v26.py", "r", encoding="utf-8") as f:
    attack_py = f.read()

# ---- Build the 5-cell notebook scaffold ----
nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": "45199530",
            "metadata": {"tags": []},
            "source": [
                "# AI Agent Security \u2014 Multi-Step Tool Attacks \u00b7 **Submission notebook v26**\n",
                "\n",
                "**v26: Replay-Recalibrated Dual-URL Attack**\n",
                "\n",
                "Fixes v25's Format Error by recalibrating the replay budget for dual-URL candidates:\n",
                "- 5 templates with dual-URL (2\u00d7 http.post per candidate = 2\u00d7 raw score density)\n",
                "- REPLAY_SAFE=0.92 (720s margin vs v25's 90s)\n",
                "- REPLAY_COST_COEF=1.15 (15% overhead buffer per candidate)\n",
                "- All candidates live-verified; no static padding\n",
                "\n",
                "**REQUIRED before submitting:** set **Accelerator = GPU T4 x2**\n",
                "(this competition rejects P100) and **Internet = Off**.\n",
            ],
        },
        {
            "cell_type": "markdown",
            "id": "e41c6e42",
            "metadata": {"tags": []},
            "source": [
                "### 1 \u00b7 Write `attack.py` (Dual-URL 5-Template Fire-Rate Race)\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "e1a2fae2",
            "metadata": {"tags": []},
            "outputs": [],
            "source": [],
        },
        {
            "cell_type": "markdown",
            "id": "eef2aaf8",
            "metadata": {"tags": []},
            "source": [
                "### 2 \u00b7 Serve \u2014 commit run writes a local submission.csv; rerun is scored\n",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "id": "d7fc850e",
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

nb["cells"][2]["source"] = cell_source

# ---- Write the notebook ----
output_path = "our_work/notebooks/stockfish_v26_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ---- Validate ----
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])
code = "".join(verify["cells"][2]["source"])
serve = "".join(verify["cells"][4]["source"])

assert cell_count == 5, f"Expected 5 cells, got {cell_count}"
assert "%%writefile /kaggle/working/attack.py" in code
assert "REPLAY_SAFE = 0.92" in code, "REPLAY_SAFE must be 0.92"
assert "REPLAY_COST_COEF = 1.15" in code, "REPLAY_COST_COEF must be 1.15"
assert "inj_close" in code
assert "inj_commentary" in code
assert "class AttackAlgorithm" in code
assert "SECRET_MARKER" in code
assert "def run(" in code
assert "{u1}" in code and "{u2}" in code, "Dual-URL templates required"
assert "JEDAttackInferenceServer" in serve
assert "KAGGLE_IS_COMPETITION_RERUN" in serve
assert "gpt_oss_public" in serve
assert "gemma_private" in serve

print("v26 notebook created and validated!")
print("  Path:", output_path)
print("  Cells:", cell_count)
print("  attack.py:", len(code), "chars")
print("  REPLAY_SAFE = 0.92 OK (720s margin)")
print("  REPLAY_COST_COEF = 1.15 OK (15% overhead buffer)")
print("  Dual-URL templates OK")
print("  5-cell scaffold OK")
print("  Id,Score placeholder OK")
