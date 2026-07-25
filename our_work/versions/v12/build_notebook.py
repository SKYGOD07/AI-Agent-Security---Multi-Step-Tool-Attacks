"""v12 Module 10: Notebook Builder (build_notebook.py).

Compiles the self-contained canonical `attack.py` into `stockfish_v12_attack.ipynb`.
Marks version clearly as v12 Deep Structural Attack Diversity Engine without updating other notebooks.
"""

import json
from pathlib import Path

def build_v12_notebook(output_dir: Path | None = None) -> Path:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if output_dir is None:
        output_dir = project_root
        
    attack_path = project_root / "attack.py"
    if not attack_path.exists():
        attack_path = project_root / "v12" / "attack.py"
        
    attack_code = attack_path.read_text(encoding="utf-8")

    cells = []

    # Cell 0: Markdown Info
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Stockfish Attack Engine v12: Deep Structural Attack Diversity & Replay-Safe Throughput\n",
            "\n",
            "A structural diversity engine built directly on the proven, high-throughput linear `v7` base (`probe -> diverse generation -> deduplicate -> budget-pack`). Strips out all online controller overhead (`bandits, model clustering, multi-stage routing`) and maximizes distinct behavioral replay yield across 6 deep strategy classes and 4 tool families.\n",
            "\n",
            "**Core v12 Upgrades & Principles:**\n",
            "1. **Zero Online Controller Bloat**: Stripped of model detection, Thompson sampling, bandits, and dynamic routing. Prioritizes maximum structural coverage and fast throughput.\n",
            "2. **6 Deep Strategy Classes (`Module 1`)**: Systematic coverage across `Strategy A (Authority)`, `Strategy B (Workflow)`, `Strategy C (Reasoning chain)`, `Strategy D (Emergency)`, `Strategy E (Maintenance)`, and `Strategy F (Debug)`.\n",
            "3. **4 Target Tool Families (`Module 1`)**: Full coverage of `EXFILTRATION`, `UNTRUSTED_TO_ACTION`, `DESTRUCTIVE_WRITE`, and `CONFUSED_DEPUTY`.\n",
            "4. **Intent-Preserving Semantic Mutations (`Module 4`)**: Generates structured variations (`formal_operation`, `sop_compliance`, `state_recovery`, `audit_diagnostic`) plus multi-turn escalation chains (`2-turn sequences`).\n",
            "5. **Semantic Behavior Signature & Deduplication (`Module 7`)**: Hashes `tool_seq|strategy_class|tool_family|payload_hash` to reject near-duplicate behaviors while retaining higher yield efficiency.\n",
            "6. **Expected Yield Efficiency Ranking (`Module 6`)**: Sorts candidate portfolio by `(prob * novelty * coverage_boost * severity) / latency`.\n",
            "7. **Replay-Safe Budget Cap (`Module 6 & 8`)**: Packs unique structural candidates up to `0.99 * 9000 seconds` (`REPLAY_SAFE`).\n",
            "8. **Adaptive Stopping (`Module 8`)**: Halts candidate generation when new semantic signatures flatten (`unproductive_streak >= 20`).\n",
            "9. **Offline Analytics & Reporting (`Module 9`)**: Computes coverage score (`100/100`), novelty score, and distribution metrics.\n",
            "10. **100% Kaggle Offline Compatibility (`Module 10`)**: Self-contained `attack.py` embedded right into Cell 1 with zero external dependencies.\n"
        ]
    })

    # Cell 1: Code - Configuration and paths
    cell1_source = """# STEP 1 — Configuration and official competition input.

import os
import sys
from pathlib import Path

sys.argv = [sys.argv[0]]

COMPETITION_SLUG = "ai-agent-security-multi-step-tool-attacks"
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

IS_COMPETITION_RERUN = bool(os.getenv("KAGGLE_IS_COMPETITION_RERUN"))
WORKING_DIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd() / "local_kaggle_working"
WORKING_DIR.mkdir(parents=True, exist_ok=True)
os.chdir(WORKING_DIR)

input_root = Path("/kaggle/input")
candidates = [
    input_root / COMPETITION_SLUG,
    input_root / "competitions" / COMPETITION_SLUG,
]

if input_root.is_dir():
    try:
        direct_children = [child for child in input_root.iterdir() if child.is_dir()]
    except OSError:
        direct_children = []
    candidates.extend(direct_children)
    for child in direct_children:
        candidates.append(child / "competitions" / COMPETITION_SLUG)

COMPETITION_ROOT = None
seen = set()
for candidate in candidates:
    try:
        resolved = candidate.resolve()
    except OSError:
        resolved = candidate
    if resolved in seen:
        continue
    seen.add(resolved)
    try:
        if (candidate / "kaggle_evaluation").is_dir():
            COMPETITION_ROOT = candidate
            break
    except OSError:
        continue

if COMPETITION_ROOT is None:
    raise RuntimeError("Attach the official 'AI Agent Security - Multi-Step Tool Attacks' competition input.")

if str(COMPETITION_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPETITION_ROOT))
if str(WORKING_DIR) not in sys.path:
    sys.path.insert(0, str(WORKING_DIR))

print("IS_COMPETITION_RERUN:", IS_COMPETITION_RERUN)
print("WORKING_DIR:", WORKING_DIR)
print("COMPETITION_ROOT:", COMPETITION_ROOT)
"""

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in cell1_source.splitlines()]
    })

    # Cell 2: Code - Write attack.py
    cell2_source = f"""# STEP 2 — Write unified self-contained attack.py to disk.

import hashlib

ATTACK_CODE = {repr(attack_code)}

ATTACK_PATH = WORKING_DIR / 'attack.py'
ATTACK_PATH.write_text(ATTACK_CODE, encoding='utf-8')
digest_bytes = hashlib.sha256(ATTACK_PATH.read_bytes()).hexdigest()
print('attack.py written to:', ATTACK_PATH)
print('size:', ATTACK_PATH.stat().st_size)
print('sha256:', digest_bytes)
"""

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in cell2_source.splitlines()]
    })

    # Cell 3: Code - Contract validation
    cell3_source = """# STEP 3 — Contract validation without model execution.

import ast
import importlib.util
import py_compile
import sys

py_compile.compile(str(ATTACK_PATH), doraise=True)
source = ATTACK_PATH.read_text(encoding="utf-8")
tree = ast.parse(source)

assert any(isinstance(node, ast.ClassDef) and node.name == "AttackAlgorithm" for node in ast.walk(tree))
print("Code review 1/2: compile and AST OK")

spec = importlib.util.spec_from_file_location("attack", str(ATTACK_PATH))
module = importlib.util.module_from_spec(spec)
sys.modules["attack"] = module
spec.loader.exec_module(module)

assert hasattr(module, "AttackAlgorithm")
algo = module.AttackAlgorithm()
assert hasattr(algo, "run")
print("Code review 2/2: imports and instantiation OK")
"""

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in cell3_source.splitlines()]
    })

    # Cell 4: Markdown - Hidden scoring info
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Hidden scoring\n",
            "\n",
            "During hidden scoring, the notebook starts the official JED inference server directly.\n"
        ]
    })

    # Cell 5: Code - Entry point
    cell5_source = """# STEP 5 — Official competition entry point.

from pathlib import Path

SUBMISSION_PATH = WORKING_DIR / "submission.csv"

if IS_COMPETITION_RERUN:
    import kaggle_evaluation.jed_attack_134815.jed_attack_inference_server as server

    print("Starting official JED inference server")
    server.JEDAttackInferenceServer().serve()
else:
    sample = COMPETITION_ROOT / "sample_submission.csv" if COMPETITION_ROOT else None
    if sample and sample.is_file():
        import shutil
        shutil.copyfile(str(sample), str(SUBMISSION_PATH))
        print("Wrote sample submission to:", SUBMISSION_PATH)
    else:
        # Fallback: write a dummy submission.csv to satisfy Kaggle check
        placeholder = "Id,Score\\ngpt_oss_public,0.0\\ngpt_oss_private,0.0\\ngemma_public,0.0\\ngemma_private,0.0\\n"
        with open(SUBMISSION_PATH, "w") as f:
            f.write(placeholder)
        print("Wrote dummy submission to:", SUBMISSION_PATH)
"""

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in cell5_source.splitlines()]
    })

    # Cell 6: Markdown - REQUIRED KAGGLE SETTINGS
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Required Kaggle settings\n",
            "\n",
            "- **Input:** `AI Agent Security - Multi-Step Tool Attacks`\n",
            "- **Internet:** Off\n",
            "- **Accelerator:** CPU or GPU (T4 or similar)\n",
            "- **Save:** `Save Version → Save & Run All`\n"
        ]
    })

    nb = {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    target_nb = output_dir / "stockfish_v12_attack.ipynb"
    with open(target_nb, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"v12 Notebook successfully built at: {target_nb}")
    return target_nb

if __name__ == "__main__":
    build_v12_notebook()
