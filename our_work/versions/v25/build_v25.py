"""Build v24 notebook: JED 5-template race attack.py in v16 notebook scaffold."""

import json

# ---- Load the decoded attack.py ----
with open("our_work/jed_attack_decoded_v25.py", "r", encoding="utf-8") as f:
    attack_py = f.read()

# ---- Build the 5-cell notebook scaffold ----
nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "id": "45199530",
            "metadata": {"tags": []},
            "source": [
                "# AI Agent Security \u2014 Multi-Step Tool Attacks \u00b7 **Submission notebook v25**\n",
                "\n",
                "**v25: Multi-Endpoint (2x URLs) Fire-Rate Race**\n",
                "\n",
                "Based on the proven v24 relay architecture, but with 2x raw score density:\n",
                "- 5 templates: plain, bare, bare_ok, inj_close, inj_commentary\n",
                "- Live fire-rate selector picks cheapest-firing template per model\n",
                "- REPLAY_SAFE=0.99 (8,910s replay cap)\n",
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
                "### 1 \u00b7 Write `attack.py` (5-Template Fire-Rate Race)\n",
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
output_path = "our_work/notebooks/stockfish_v25_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# ---- Validate ----
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])
code = "".join(verify["cells"][2]["source"])
serve = "".join(verify["cells"][4]["source"])

assert cell_count == 5
assert "%%writefile /kaggle/working/attack.py" in code
assert "REPLAY_SAFE = 0.99" in code
assert "inj_close" in code
assert "inj_commentary" in code
assert "class AttackAlgorithm" in code
assert "SECRET_MARKER" in code
assert "def run(" in code
assert "JEDAttackInferenceServer" in serve
assert "KAGGLE_IS_COMPETITION_RERUN" in serve
assert "gpt_oss_public" in serve
assert "gemma_private" in serve

print("v25 notebook created and validated!")
print("  Path:", output_path)
print("  Cells:", cell_count)
print("  attack.py:", len(code), "chars")
print("  REPLAY_SAFE = 0.99 OK")
print("  5 templates OK")
print("  5-cell scaffold OK")
print("  Id,Score placeholder OK")
