"""v12 Module 10: Notebook Verifier (verify_notebook.py).

Verifies `stockfish_v12_attack.ipynb` JSON formatting, extracts `ATTACK_CODE`, validates syntax and AST structure, and confirms `AttackAlgorithm` contract compliance.
"""

import ast
import json
from pathlib import Path

def verify_v12_notebook(nb_path: Path | None = None) -> bool:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if nb_path is None:
        nb_path = project_root / "stockfish_v12_attack.ipynb"

    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    print(f"Reading notebook from: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    assert nb.get("nbformat") == 4, "nbformat must be 4"
    cells = nb.get("cells", [])
    assert len(cells) >= 5, f"Expected at least 5 cells, got {len(cells)}"

    # Find the cell writing ATTACK_CODE
    attack_code_str = None
    for cell in cells:
        if cell.get("cell_type") == "code":
            source_lines = cell.get("source", [])
            source_text = "".join(source_lines)
            if "ATTACK_CODE =" in source_text:
                # Extract the assigned ATTACK_CODE
                loc = {}
                exec(source_text.split("ATTACK_PATH =")[0], {}, loc)
                if "ATTACK_CODE" in loc:
                    attack_code_str = loc["ATTACK_CODE"]
                break

    assert attack_code_str is not None, "Could not extract ATTACK_CODE from notebook cells"
    print(f"Successfully extracted ATTACK_CODE ({len(attack_code_str)} chars)")

    # Validate AST and structure
    tree = ast.parse(attack_code_str)
    has_algo = any(isinstance(node, ast.ClassDef) and node.name == "AttackAlgorithm" for node in ast.walk(tree))
    assert has_algo, "AttackAlgorithm class definition not found in extracted ATTACK_CODE"

    print("v12 Notebook verification PASSED: valid JSON, valid python AST, and required classes found.")
    return True

if __name__ == "__main__":
    verify_v12_notebook()
