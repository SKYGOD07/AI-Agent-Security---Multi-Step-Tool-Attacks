"""v13 Module 10: Standalone Notebook Builder (build_notebook.py).

Compiles and builds `stockfish_v13_attack.ipynb` adhering strictly to the user's instructions:
1. One `attack.py` embedded inside Cell 2 (`ATTACK_CODE = ...`).
2. No extra modules, zero offline analytics, zero `SandboxEnv` imports.
3. Pure syntax and AST verification in Step 3 (no `importlib` execution, no `AttackAlgorithm()` instantiation inside notebook cells).
4. Does not modify or overwrite any prior competition notebooks (`v12`, `v11`, `v9`, `v8`, `v7`, `v5`, `v4`, `v3`).
"""

import json
from pathlib import Path

def create_v13_notebook(output_path: Path | None = None) -> Path:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if output_path is None:
        output_path = project_root / "stockfish_v13_attack.ipynb"

    attack_py_path = project_root / "attack.py"
    if not attack_py_path.exists():
        raise FileNotFoundError(f"Missing {attack_py_path}")

    attack_code = attack_py_path.read_text(encoding="utf-8")
    escaped_attack_code = repr(attack_code)

    cell_1_md = [
        "# Stockfish Attack Discovery Engine v13: Replay-Throughput & Multi-Family Diversity Optimizer\n",
        "\n",
        "A true architectural reset designed to maximize Kaggle leaderboard score by returning to the proven `v7` (`84.240` public score) philosophy and eliminating all online controller complexity, multi-module overhead, and notebook startup risks.\n",
        "\n",
        "**Core v13 Architectural Principles:**\n",
        "1. **One Self-Contained `attack.py` (`~360 lines`)**: Zero external modules, zero offline analytics, zero report generation, zero `ClusteringEngine`/bandits.\n",
        "2. **Zero Local SDK Emulation**: No local sandbox environment imports or internal mock references. Pure adherence to `AttackEnvProtocol` (`env.interact` / `env.export_trace_dict`).\n",
        "3. **Zero Startup Execution Risk**: Removed `importlib.util.exec_module` and `AttackAlgorithm()` construction from notebook cells (`Step 3` is now purely syntax & AST check without dynamic imports).\n",
        "4. **Replay-Throughput Pipeline (`v7 Base`)**: Pipeline structured cleanly as `probe -> select -> seed -> fill -> thin explore -> dedup -> compact portfolio`.\n",
        "5. **Multi-Family Template Coverage**: Probes and fills across all 4 target predicate families (`EXFILTRATION`, `UNTRUSTED_EXEC`, `DESTRUCTIVE_WRITE`, `CONFUSED_DEPUTY`) to maximize predicate violation diversity.\n",
        "6. **Replay-Safe Budgeting**: Estimates replay costs from measured successful probe latencies and caps returned candidates at `0.99 * 9000s` (`REPLAY_SAFE`).\n"
    ]

    cell_2_code = [
        "# STEP 1 — Configuration and official competition input setup.\n",
        "\n",
        "import os\n",
        "import sys\n",
        "from pathlib import Path\n",
        "\n",
        "sys.argv = [sys.argv[0]]\n",
        "\n",
        "COMPETITION_SLUG = \"ai-agent-security-multi-step-tool-attacks\"\n",
        "os.environ.setdefault(\"TOKENIZERS_PARALLELISM\", \"false\")\n",
        "\n",
        "IS_COMPETITION_RERUN = bool(os.getenv(\"KAGGLE_IS_COMPETITION_RERUN\"))\n",
        "WORKING_DIR = Path(\"/kaggle/working\") if Path(\"/kaggle/working\").exists() else Path.cwd() / \"local_kaggle_working\"\n",
        "WORKING_DIR.mkdir(parents=True, exist_ok=True)\n",
        "os.chdir(WORKING_DIR)\n",
        "\n",
        "input_root = Path(\"/kaggle/input\")\n",
        "candidates = [\n",
        "    input_root / COMPETITION_SLUG,\n",
        "    input_root / \"competitions\" / COMPETITION_SLUG,\n",
        "]\n",
        "\n",
        "if input_root.is_dir():\n",
        "    try:\n",
        "        direct_children = [child for child in input_root.iterdir() if child.is_dir()]\n",
        "    except OSError:\n",
        "        direct_children = []\n",
        "    candidates.extend(direct_children)\n",
        "    for child in direct_children:\n",
        "        candidates.append(child / \"competitions\" / COMPETITION_SLUG)\n",
        "\n",
        "COMPETITION_ROOT = None\n",
        "seen = set()\n",
        "for candidate in candidates:\n",
        "    try:\n",
        "        resolved = candidate.resolve()\n",
        "    except OSError:\n",
        "        resolved = candidate\n",
        "    if resolved in seen:\n",
        "        continue\n",
        "    seen.add(resolved)\n",
        "    try:\n",
        "        if (candidate / \"kaggle_evaluation\").is_dir():\n",
        "            COMPETITION_ROOT = candidate\n",
        "            break\n",
        "    except OSError:\n",
        "        continue\n",
        "\n",
        "if COMPETITION_ROOT is None:\n",
        "    raise RuntimeError(\"Attach the official 'AI Agent Security - Multi-Step Tool Attacks' competition input.\")\n",
        "\n",
        "if str(COMPETITION_ROOT) not in sys.path:\n",
        "    sys.path.insert(0, str(COMPETITION_ROOT))\n",
        "if str(WORKING_DIR) not in sys.path:\n",
        "    sys.path.insert(0, str(WORKING_DIR))\n",
        "\n",
        "print(\"IS_COMPETITION_RERUN:\", IS_COMPETITION_RERUN)\n",
        "print(\"WORKING_DIR:\", WORKING_DIR)\n",
        "print(\"COMPETITION_ROOT:\", COMPETITION_ROOT)\n"
    ]

    cell_3_code = [
        "# STEP 2 — Write unified self-contained attack.py to disk.\n",
        "\n",
        "import hashlib\n",
        "\n",
        f"ATTACK_CODE = {escaped_attack_code}\n",
        "\n",
        "ATTACK_PATH = WORKING_DIR / 'attack.py'\n",
        "ATTACK_PATH.write_text(ATTACK_CODE, encoding='utf-8')\n",
        "digest_bytes = hashlib.sha256(ATTACK_PATH.read_bytes()).hexdigest()\n",
        "print('attack.py written to:', ATTACK_PATH)\n",
        "print('size:', ATTACK_PATH.stat().st_size)\n",
        "print('sha256:', digest_bytes)\n"
    ]

    cell_4_code = [
        "# STEP 3 — Pure Syntax & AST Verification (No Runtime Import / No Constructor Execution).\n",
        "\n",
        "import ast\n",
        "import py_compile\n",
        "\n",
        "py_compile.compile(str(ATTACK_PATH), doraise=True)\n",
        "source = ATTACK_PATH.read_text(encoding=\"utf-8\")\n",
        "tree = ast.parse(source)\n",
        "\n",
        "assert any(isinstance(node, ast.ClassDef) and node.name == \"AttackAlgorithm\" for node in ast.walk(tree)), \"AttackAlgorithm class definition missing!\"\n",
        "print(\"Code review PASSED: Python syntax compilation and AST check OK without runtime instantiation.\")\n"
    ]

    cell_5_md = [
        "## Hidden scoring / Official competition entry point\n",
        "\n",
        "During hidden scoring, the notebook writes `attack.py` and immediately starts the official JED inference server (`JEDAttackInferenceServer().serve()`).\n"
    ]

    cell_6_code = [
        "# STEP 4 — Official competition entry point.\n",
        "\n",
        "from pathlib import Path\n",
        "\n",
        "SUBMISSION_PATH = WORKING_DIR / \"submission.csv\"\n",
        "\n",
        "if IS_COMPETITION_RERUN:\n",
        "    import kaggle_evaluation.jed_attack_134815.jed_attack_inference_server as server\n",
        "\n",
        "    print(\"Starting official JED inference server\")\n",
        "    server.JEDAttackInferenceServer().serve()\n",
        "else:\n",
        "    sample = COMPETITION_ROOT / \"sample_submission.csv\" if COMPETITION_ROOT else None\n",
        "    if sample and sample.is_file():\n",
        "        import shutil\n",
        "        shutil.copyfile(str(sample), str(SUBMISSION_PATH))\n",
        "        print(\"Wrote sample submission to:\", SUBMISSION_PATH)\n",
        "    else:\n",
        "        placeholder = \"Id,Score\\ngpt_oss_public,0.0\\ngpt_oss_private,0.0\\ngemma_public,0.0\\ngemma_private,0.0\\n\"\n",
        "        with open(SUBMISSION_PATH, \"w\") as f:\n",
        "            f.write(placeholder)\n",
        "        print(\"Wrote dummy submission to:\", SUBMISSION_PATH)\n"
    ]

    cell_7_md = [
        "## Required Kaggle settings\n",
        "\n",
        "- **Input:** `AI Agent Security - Multi-Step Tool Attacks`\n",
        "- **Internet:** Off\n",
        "- **Accelerator:** CPU or GPU (T4 or similar)\n",
        "- **Save:** `Save Version -> Save & Run All`\n"
    ]

    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": cell_1_md},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell_2_code},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell_3_code},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell_4_code},
        {"cell_type": "markdown", "metadata": {}, "source": cell_5_md},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell_6_code},
        {"cell_type": "markdown", "metadata": {}, "source": cell_7_md},
    ]

    notebook_dict = {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notebook_dict, f, indent=1)

    print(f"v13 Standalone Notebook built at: {output_path}")
    return output_path

if __name__ == "__main__":
    create_v13_notebook()
