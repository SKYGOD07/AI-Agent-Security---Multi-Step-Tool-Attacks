import json
import os

def build_notebook(source_py_path, output_ipynb_path):
    with open(source_py_path, 'r', encoding='utf-8') as f:
        code = f.read()

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# AI Agent Security v10 Attack Setup\n", "This notebook contains the offline attack generator code."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["%%writefile attack.py\n"] + [line + "\n" for line in code.split("\n")]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "import pandas as pd\n",
                "pd.DataFrame([{'Id': 'dummy', 'Score': 0}]).to_csv('submission.csv', index=False)\n",
                "print('Created dummy submission.csv to satisfy Kaggle offline notebook requirements.')\n"
            ]
        }
    ]

    notebook = {
        "cells": cells,
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
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    with open(output_ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build Kaggle Submission Notebook")
    parser.add_argument("--source", default="attack.py")
    parser.add_argument("--output", default="stockfish_v10_attack.ipynb")
    args = parser.parse_args()

    source = args.source
    out = args.output

    # Try resolving relative paths if needed
    if not os.path.exists(source) and os.path.exists(os.path.join(os.path.dirname(__file__), source)):
        source = os.path.join(os.path.dirname(__file__), source)

    build_notebook(source, out)
    print(f"Notebook {out} successfully built from {source}.")
