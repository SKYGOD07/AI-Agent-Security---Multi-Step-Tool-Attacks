"""v16 Notebook Verifier: ensures structure matches 88.560 baseline."""

import json
from pathlib import Path


def verify_v16_notebook(nb_path: Path | None = None) -> bool:
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    if nb_path is None:
        nb_path = project_root / "stockfish_v16_attack.ipynb"

    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    print(f"Reading notebook from: {nb_path}")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Check nbformat
    assert nb.get("nbformat") == 4, "nbformat must be 4"

    cells = nb.get("cells", [])

    # Expected: 5 cells (markdown, markdown, code, markdown, code)
    assert len(cells) == 5, f"Expected exactly 5 cells, got {len(cells)}"
    assert cells[0]["cell_type"] == "markdown", "Cell 1 must be markdown"
    assert cells[1]["cell_type"] == "markdown", "Cell 2 must be markdown"
    assert cells[2]["cell_type"] == "code", "Cell 3 must be code"
    assert cells[3]["cell_type"] == "markdown", "Cell 4 must be markdown"
    assert cells[4]["cell_type"] == "code", "Cell 5 must be code"
    print(f"  Structure: 5 cells (3 markdown, 2 code) ✓")

    # Check Cell 3 has %%writefile
    cell3_src = "".join(cells[2].get("source", []))
    assert "%%writefile /kaggle/working/attack.py" in cell3_src, "Cell 3 must contain %%writefile"
    assert "Live per-model validation-fill" in cell3_src, "Cell 3 must contain attack code"
    print(f"  Cell 3: %%writefile /kaggle/working/attack.py + inline code ✓")

    # Check Cell 5 has IS_RERUN gating
    cell5_src = "".join(cells[4].get("source", []))
    assert "KAGGLE_IS_COMPETITION_RERUN" in cell5_src, "Cell 5 must check KAGGLE_IS_COMPETITION_RERUN"
    assert "if IS_RERUN:" in cell5_src, "Cell 5 must have 'if IS_RERUN:'"
    assert "server.serve()" in cell5_src, "Cell 5 must call server.serve()"
    print(f"  Cell 5: IS_RERUN gating + JEDAttackInferenceServer().serve() ✓")

    print("\nv16 Notebook verification PASSED: exact replica of 88.560 structure.")
    return True


if __name__ == "__main__":
    verify_v16_notebook()
