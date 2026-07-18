import json
import argparse
import sys
import os

def verify_notebook(notebook_path):
    if not os.path.exists(notebook_path):
        print(f"Error: {notebook_path} not found.")
        sys.exit(1)

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    has_writefile = False
    has_submission = False

    for cell in cells:
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            if "%%writefile attack.py" in source:
                has_writefile = True
            if "submission.csv" in source and "Id" in source and "Score" in source:
                has_submission = True

    if not has_writefile:
        print("Error: %%writefile attack.py cell is missing.")
        sys.exit(1)

    if not has_submission:
        print("Error: submission.csv creation code is missing or incorrect.")
        sys.exit(1)

    print(f"Success: {notebook_path} is valid.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Kaggle Submission Notebook")
    parser.add_argument("--notebook", default="stockfish_v10_attack.ipynb")
    args = parser.parse_args()

    nb = args.notebook
    if not os.path.exists(nb) and os.path.exists(os.path.join(os.path.dirname(__file__), nb)):
        nb = os.path.join(os.path.dirname(__file__), nb)

    verify_notebook(nb)
