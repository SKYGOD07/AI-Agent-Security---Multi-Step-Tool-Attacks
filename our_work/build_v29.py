"""Build v29 notebook: ai-agent-security-90 architecture (90.09 score) + defensive scaffolding."""

import base64
import json

# ---- Load the decoded attack.py ----
with open("our_work/jed_attack_decoded_v29.py", "r", encoding="utf-8") as f:
    attack_py = f.read()

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

output_path = "our_work/notebooks/stockfish_v29_attack.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

# Validate
with open(output_path, "r", encoding="utf-8") as f:
    verify = json.load(f)

cell_count = len(verify["cells"])
b64_line = [l for l in verify["cells"][1]["source"] if "ATTACK_PY_B64" in l and "=" in l][0]
b64_val = b64_line.split('"')[1]
decoded = base64.b64decode(b64_val).decode("utf-8")

assert cell_count == 3
assert "BURST_K = 2" in decoded, "BURST_K must be 2 for gemma fast row"
assert "SLOW_MULTIPOST_N = 4" in decoded, "SLOW_MULTIPOST_N must be 4 for gpt_oss slow row"
assert "MARGIN_S = 47.0" in decoded
assert "REPLAY_SAFE_FRAC = 0.97" in decoded
assert "def __init__" in decoded
assert "_forge_plan_msg" in decoded
assert "_burst_msg" in decoded

print("v29 notebook created and validated!")
print(f"  Path: {output_path}")
print(f"  BURST_K = 2 (gemma fast row)")
print(f"  SLOW_MULTIPOST_N = 4 (gpt_oss slow row)")
