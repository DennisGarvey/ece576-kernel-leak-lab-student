# Kernel Leak Lab

Choose the notebook assigned by your instructor:

- **Beginner — `Kernel_Leak_Lab.ipynb`:** supplied calculations, statistics, rankings, and plotting with explanations.
- **Advanced — `Kernel_Leak_Lab_Advanced.ipynb`:** implement all leakage calculations, NumPy operations, statistics, rankings, and graphs yourself. Each section specifies required code, outputs, and explanations. Both notebooks use the same `Investigation` object from `lab.py`. The advanced notebook leaves the analysis code blank.

Both versions use the same instance and packets.

Use Python 3.10 or newer. In this folder, run:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab Kernel_Leak_Lab.ipynb
```

To open the advanced version, use `python -m jupyterlab Kernel_Leak_Lab_Advanced.ipynb` instead.

Open your selected notebook from this folder so its packet paths resolve. Read the instructions, run cells in order, and edit your acquisition choices, previous guesses, final tuple, and evidence notes. Re-running acquisition spends another batch. Restarting the kernel resets your ledger; preserve one run for submission.

Submit your completed notebook and `submission.json` (beginner) or `submission-advanced.json` (advanced). The notebook explains each calculation and the meaning of its output. Record your acquisition predictions and candidate evidence as you investigate WPInference.
