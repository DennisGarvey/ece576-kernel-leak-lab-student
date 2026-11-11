# Kernel Leak Lab

Use Correlation Power Analysis to recover three weights from WPInference power traces. Choose either notebook.

- `Kernel_Leak_Lab.ipynb` provides the calculations and plots for the beginner lab.
- `Kernel_Leak_Lab_Advanced.ipynb` specifies the calculations, plots, and explanations to produce for the advanced lab.

## Set up

Clone the student repository or select **Code → Download ZIP** on GitHub and extract the files. Open the project directory in a terminal and run the following commands with Python 3.10 or newer.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start JupyterLab with `python -m jupyterlab` and open the notebook you chose. Keep the notebook in this directory so it can load `manifest.json` and `packets/`.

## Run and submit

Run the notebook cells in order. Record your prediction before acquiring each batch of traces. Re-running the acquisition cell adds another batch and uses more of your budget. Restarting the Python kernel resets the acquisition ledger, so keep one recorded run for submission.

Submit the completed notebook and the exported `submission.json` for the beginner lab or `submission-advanced.json` for the advanced lab.
