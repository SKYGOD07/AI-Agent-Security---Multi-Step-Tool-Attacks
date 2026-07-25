"""v14 Module 10: Notebook Verifier (verify_notebook.py).

Verifies `stockfish_v14_attack.ipynb` JSON formatting, decodes `ATTACK_PY_B64`, validates Python syntax compilation and AST structure without instantiating or running model code.
"""

import ast
import base64
import json
from pathlib import Path

def verify_v14_notebook(nb_path: Path | None = None) -> bool:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if nb_path is None:
        nb_path = project_root / "stockfish_v14_attack.ipynb"

    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    print(f"Reading notebook from: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    assert nb.get("nbformat") == 4, "nbformat must be 4"
    cells = nb.get("cells", [])
    assert len(cells) >= 4, f"Expected at least 4 cells, got {len(cells)}"

    attack_b64_str = None
    for cell in cells:
        if cell.get("cell_type") == "code":
            source_lines = cell.get("source", [])
            source_text = "".join(source_lines)
            if "ATTACK_PY_B64 =" in source_text:
                for line in source_text.splitlines():
                    if "ATTACK_PY_B64 =" in line:
                        attack_b64_str = line.split('"')[1]
                        break
                break

    assert attack_b64_str is not None, "Could not extract ATTACK_PY_B64 from notebook cells"
    attack_code_str = base64.b64decode(attack_b64_str).decode("utf-8")
    print(f"Successfully extracted and decoded ATTACK_PY_B64 ({len(attack_code_str)} chars, {len(attack_code_str.splitlines())} lines)")

    # Validate AST and structure
    tree = ast.parse(attack_code_str)
    has_algo = any(isinstance(node, ast.ClassDef) and node.name == "AttackAlgorithm" for node in ast.walk(tree))
    assert has_algo, "AttackAlgorithm class definition not found in decoded attack code"

    # Verify NO local sandbox / internal SDK imports in AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "sandbox" not in alias.name.lower(), f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module is not None and "sandbox" not in node.module.lower(), f"Forbidden import from: {node.module}"

    print("v14 Notebook verification PASSED: valid JSON, valid base64 decode, valid python AST, zero local sandbox imports, and required classes found.")
    return True

if __name__ == "__main__":
    verify_v14_notebook()
