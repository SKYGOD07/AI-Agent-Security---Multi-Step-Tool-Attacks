import json
import py_compile
from pathlib import Path

def verify_v20():
    project_root = Path(r"c:\OPENAI AI AGENT CYBERSEC\our_work")
    attack_py = project_root / "v20" / "attack_v20.py"
    nb_path = project_root / "stockfish_v20_attack.ipynb"

    print("1. Verifying attack_v20.py syntax...")
    py_compile.compile(str(attack_py), doraise=True)
    print("   -> Syntax OK")

    print("2. Verifying stockfish_v20_attack.ipynb structure...")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb["cells"]
    assert len(cells) == 5, f"Expected 5 cells, got {len(cells)}"

    cell3_src = "".join(cells[2]["source"])
    assert "%%writefile /kaggle/working/attack.py" in cell3_src, "Missing %%writefile in cell 3"

    cell5_src = "".join(cells[4]["source"])
    assert "IS_RERUN" in cell5_src, "Missing IS_RERUN in cell 5"
    assert "JEDAttackInferenceServer" in cell5_src, "Missing JEDAttackInferenceServer in cell 5"
    assert "submission.csv" in cell5_src, "Missing submission.csv in cell 5"
    assert "Id" in cell5_src and "Score" in cell5_src, "Missing Id/Score schema in cell 5"

    print("   -> Notebook scaffold OK")
    print("ALL VERIFICATIONS PASSED FOR V20.")

if __name__ == "__main__":
    verify_v20()
