"""v15 Notebook Builder: exact 3-cell code-only structure matching proven resubmission.

Copies the EXACT notebook structure from ai-agent-sec-another-approach-resubmission.ipynb
(scored 85.950) and jedforce-1.ipynb (scored 84.870):
- Cell 1: import + path discovery + print('Setup complete')
- Cell 2: ATTACK_PY_B64 decode + write to /kaggle/working/attack.py
- Cell 3: submission.csv placeholder + JEDAttackInferenceServer().serve()

NO markdown cells. NO AST verification cells. NO dynamic paths.
"""

import base64
import json
from pathlib import Path


def create_v15_notebook(output_path: Path | None = None) -> Path:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if output_path is None:
        output_path = project_root / "stockfish_v15_attack.ipynb"

    attack_py_path = project_root / "attack.py"
    if not attack_py_path.exists():
        raise FileNotFoundError(f"Missing {attack_py_path}")

    attack_bytes = attack_py_path.read_bytes()
    attack_b64 = base64.b64encode(attack_bytes).decode("ascii")

    # Cell 1: EXACT copy of resubmission Cell 1 structure
    cell_1 = {
        "cell_type": "code",
        "execution_count": None,
        "id": "51d8e7ba",
        "metadata": {"tags": []},
        "outputs": [],
        "source": [
            "# R1-009\n",
            "import sys, os, base64, glob\n",
            "from pathlib import Path\n",
            "sys.argv = [sys.argv[0]]\n",
            "for candidate in glob.glob('/kaggle/input/**/kaggle_evaluation', recursive=True):\n",
            "    dataset_root = str(Path(candidate).parent)\n",
            "    if dataset_root not in sys.path:\n",
            "        sys.path.insert(0, dataset_root)\n",
            "    print(f'Dataset root: {dataset_root}')\n",
            "    break\n",
            "print('Setup complete')\n"
        ]
    }

    # Cell 2: ATTACK_PY_B64 decode + write to HARDCODED /kaggle/working/attack.py
    cell_2 = {
        "cell_type": "code",
        "execution_count": None,
        "id": "ade865e2",
        "metadata": {"tags": []},
        "outputs": [],
        "source": [
            "import base64\n",
            f"ATTACK_PY_B64 = \"{attack_b64}\"\n",
            "attack_bytes = base64.b64decode(ATTACK_PY_B64)\n",
            "with open('/kaggle/working/attack.py','wb') as f:\n",
            "    f.write(attack_bytes)\n",
            "print(f'attack.py written: {len(attack_bytes)} bytes')\n"
        ]
    }

    # Cell 3: submission.csv + JEDAttackInferenceServer (EXACT copy of resubmission Cell 3)
    cell_3 = {
        "cell_type": "code",
        "execution_count": None,
        "id": "33cda06d",
        "metadata": {"tags": []},
        "outputs": [],
        "source": [
            "from pathlib import Path\n",
            "placeholder = 'Id,Score\\ngpt_oss_public,0.0\\ngpt_oss_private,0.0\\ngemma_public,0.0\\ngemma_private,0.0\\n'\n",
            "(Path('/kaggle/working') / 'submission.csv').write_text(placeholder)\n",
            "print('submission.csv placeholder written')\n",
            "from kaggle_evaluation.jed_attack_134815.jed_attack_inference_server import JEDAttackInferenceServer\n",
            "JEDAttackInferenceServer().serve()\n"
        ]
    }

    notebook_dict = {
        "cells": [cell_1, cell_2, cell_3],
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

    print(f"v15 Notebook built at: {output_path}")
    print(f"  Cells: {len(notebook_dict['cells'])} (all code, zero markdown)")
    print(f"  attack.py size: {len(attack_bytes)} bytes")
    return output_path


if __name__ == "__main__":
    create_v15_notebook()
