"""v20 Notebook Builder: Compact Replay-Portfolio Engine

Generates stockfish_v20_attack.ipynb following the strict 5-cell scaffold.
- No notebook-side import or execution of attack.py
- No SandboxEnv imports
- Gated behind KAGGLE_IS_COMPETITION_RERUN
- Produces exact submission.csv schema (Id,Score)
"""

import json
from pathlib import Path


def create_v20_notebook(output_path: Path | None = None) -> Path:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if output_path is None:
        output_path = project_root / "stockfish_v20_attack.ipynb"

    attack_py_path = project_root / "v20" / "attack_v20.py"
    if not attack_py_path.exists():
        raise FileNotFoundError(f"Missing {attack_py_path}")

    attack_source = attack_py_path.read_text(encoding="utf-8")

    # Cell 1: Markdown description
    cell_1 = {
        "cell_type": "markdown",
        "id": "45199530",
        "metadata": {"tags": []},
        "source": [
            "# AI Agent Security — Multi-Step Tool Attacks · **Submission notebook v20**\n",
            "\n",
            "**Compact Replay-Portfolio Engine (v20):**\n",
            "- 5-template probe (5 reps) with effective cost ranking\n",
            "- Seeded probe candidates & replay-safe fill (capped by measured latency ≤ 8910s)\n",
            "- Compact signature archive: deduplication by replay signature\n",
            "- Controlled live diversity layer with dynamic decay\n",
            "\n",
            "**REQUIRED before submitting:** set **Accelerator = GPU T4 x2**\n",
            "and **Internet = Off**.\n"
        ]
    }

    # Cell 2: Markdown section header
    cell_2 = {
        "cell_type": "markdown",
        "id": "e41c6e42",
        "metadata": {"tags": []},
        "source": [
            "### 1 · Write `attack.py` (v20 Compact Replay-Portfolio Engine)\n"
        ]
    }

    # Cell 3: %%writefile attack.py
    writefile_source = ["%%writefile /kaggle/working/attack.py\n"]
    for line in attack_source.splitlines(keepends=True):
        writefile_source.append(line)

    cell_3 = {
        "cell_type": "code",
        "execution_count": None,
        "id": "e1a2fae2",
        "metadata": {"tags": []},
        "outputs": [],
        "source": writefile_source
    }

    # Cell 4: Markdown section header
    cell_4 = {
        "cell_type": "markdown",
        "id": "eef2aaf8",
        "metadata": {"tags": []},
        "source": [
            "### 2 · Serve — commit run writes a local submission.csv; rerun is scored\n"
        ]
    }

    # Cell 5: Server start with KAGGLE_IS_COMPETITION_RERUN gating
    cell_5 = {
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
            "    server.serve()\n",
            "else:\n",
            "    import csv\n",
            "    with open(\"submission.csv\", \"w\", newline=\"\") as fh:\n",
            "        w = csv.writer(fh); w.writerow([\"Id\", \"Score\"]); w.writerows([[\"gpt_oss_public\", 0.0], [\"gpt_oss_private\", 0.0], [\"gemma_public\", 0.0], [\"gemma_private\", 0.0]])\n",
            "    print(\"placeholder submission.csv written. Set Accelerator = GPU T4 x2, then Submit.\")\n"
        ]
    }

    notebook_dict = {
        "cells": [cell_1, cell_2, cell_3, cell_4, cell_5],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notebook_dict, f, indent=1)

    print(f"v20 Notebook built at: {output_path}")
    print(f"  Cells: {len(notebook_dict['cells'])} (3 markdown, 2 code)")
    attack_lines = len(attack_source.splitlines())
    print(f"  attack.py: {attack_lines} lines")
    return output_path


if __name__ == "__main__":
    create_v20_notebook()
