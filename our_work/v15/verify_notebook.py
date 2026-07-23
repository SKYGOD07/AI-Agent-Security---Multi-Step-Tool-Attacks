"""v15 Notebook Verifier: ensures notebook structure matches proven resubmission format."""

import ast
import base64
import json
from pathlib import Path


def verify_v15_notebook(nb_path: Path | None = None) -> bool:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if nb_path is None:
        nb_path = project_root / "stockfish_v15_attack.ipynb"

    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    print(f"Reading notebook from: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Check nbformat
    assert nb.get("nbformat") == 4, "nbformat must be 4"

    cells = nb.get("cells", [])

    # CRITICAL: Must have exactly 3 cells, ALL code (no markdown)
    assert len(cells) == 3, f"CRITICAL: Expected exactly 3 cells, got {len(cells)}"
    for i, cell in enumerate(cells):
        assert cell["cell_type"] == "code", f"CRITICAL: Cell {i} must be 'code', got '{cell['cell_type']}'"
    print(f"  Structure: 3 code cells, zero markdown ✓")

    # Check Cell 1 has path setup
    cell1_src = "".join(cells[0].get("source", []))
    assert "kaggle_evaluation" in cell1_src, "Cell 1 must contain kaggle_evaluation path setup"
    assert "Setup complete" in cell1_src, "Cell 1 must print 'Setup complete'"
    print(f"  Cell 1: Path setup ✓")

    # Check Cell 2 has ATTACK_PY_B64
    cell2_src = "".join(cells[1].get("source", []))
    assert "ATTACK_PY_B64" in cell2_src, "Cell 2 must contain ATTACK_PY_B64"
    assert "/kaggle/working/attack.py" in cell2_src, "Cell 2 must write to /kaggle/working/attack.py"
    print(f"  Cell 2: ATTACK_PY_B64 + write to /kaggle/working/attack.py ✓")

    # Decode and verify attack.py
    for line in cell2_src.splitlines():
        if "ATTACK_PY_B64 =" in line:
            b64_val = line.split('"')[1]
            attack_code = base64.b64decode(b64_val).decode("utf-8")
            tree = ast.parse(attack_code)
            has_algo = any(isinstance(n, ast.ClassDef) and n.name == "AttackAlgorithm" for n in ast.walk(tree))
            assert has_algo, "AttackAlgorithm class not found in decoded attack.py"
            print(f"  Decoded attack.py: {len(attack_code)} chars, {len(attack_code.splitlines())} lines, AttackAlgorithm found ✓")
            break

    # Check Cell 3 has server start
    cell3_src = "".join(cells[2].get("source", []))
    assert "submission.csv" in cell3_src, "Cell 3 must write submission.csv"
    assert "JEDAttackInferenceServer" in cell3_src, "Cell 3 must start JEDAttackInferenceServer"
    assert ".serve()" in cell3_src, "Cell 3 must call .serve()"
    print(f"  Cell 3: submission.csv + JEDAttackInferenceServer().serve() ✓")

    # Check kernelspec metadata exists
    meta = nb.get("metadata", {})
    assert "kernelspec" in meta, "Missing kernelspec metadata"
    print(f"  Metadata: kernelspec present ✓")

    print("\nv15 Notebook verification PASSED: exact 3-cell code-only structure matching proven resubmission.")
    return True


if __name__ == "__main__":
    verify_v15_notebook()
