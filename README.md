# Kernel Leak Lab

Both notebooks use Correlation Power Analysis to recover the same three model weights from WPInference power traces. Choose the track that fits your coding experience.

- **Beginner** (`Kernel_Leak_Lab.ipynb`) provides more code, including the calculations and plots, so you can focus on interpreting the results.
- **Advanced** (`Kernel_Leak_Lab_Advanced.ipynb`) asks you to write the analysis and plotting code. Choose this track if you have prior coding experience and are comfortable writing Python.

If you're unsure which track to choose, start with the advanced notebook. If you get stuck, look at the beginner notebook for hints or switch to it for a more guided experience.

## Set up

Clone the student repository or select **Code → Download ZIP** on GitHub and extract the files. Open the project directory in a terminal and run the following commands with Python 3.10 or newer.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

### macOS and Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab
```

In JupyterLab, open the notebook you chose. Keep the notebook in the project directory so it can load `manifest.json` and `packets/`.

## Run and submit

Run the notebook cells in order. Record your prediction before acquiring each batch of traces. Re-running the acquisition cell adds another batch and uses more of your budget. Restarting the Python kernel resets the acquisition ledger, so keep one recorded run for submission.

Submit the completed notebook and the exported `submission.json` for the beginner lab or `submission-advanced.json` for the advanced lab.
