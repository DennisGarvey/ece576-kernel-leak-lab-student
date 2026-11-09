"""Public analysis and packet interface. Contains no challenge answers."""
import json
from pathlib import Path
import numpy as np

CANDIDATES = np.arange(-128, 128, dtype=np.int64)
_HW = np.array([i.bit_count() for i in range(256)], dtype=np.uint8)


def hw32(value):
    value = np.asarray(value, dtype=np.int64) & 0xffffffff
    return sum(_HW[(value >> s) & 255] for s in (0, 8, 16, 24)).astype(float)


def predictions(inputs, prefix, index, model="HD"):
    if len(prefix) != index:
        raise ValueError("Prefix must contain every weight before the target.")
    if model not in ("HD", "HW"):
        raise ValueError("Choose HD or HW.")
    x = inputs.astype(np.int64)
    old = x[:, :index] @ np.asarray(prefix, dtype=np.int64)
    new = old[:, None] + x[:, index, None] * CANDIDATES
    return hw32(old[:, None] ^ new) if model == "HD" else hw32(new)


def cpa(inputs, traces, prefix, index, model="HD"):
    h = predictions(inputs, prefix, index, model)
    h -= h.mean(axis=0)
    y = traces[:, 6 + 12*index].astype(float)
    y -= y.mean()
    den = np.sqrt((h*h).sum(axis=0) * (y*y).sum())
    return np.divide(h.T @ y, den, out=np.full(256, np.nan), where=den > 0)


def ranking(inputs, traces, prefix, index, model="HD"):
    scores = cpa(inputs, traces, prefix, index, model)
    order = np.argsort(np.nan_to_num(scores, nan=-np.inf))[::-1]
    return [{"weight": int(CANDIDATES[g]), "r": float(scores[g])}
            for g in order if np.isfinite(scores[g])][:10]


def plot_trace(traces, row=0):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(traces[row], label=f"Execution {row}")
    for j in range(9):
        ax.axvline(6 + 12*j, alpha=.2, color="black")
    ax.set(xlabel="Sample index (count)", ylabel="Simulated power (arbitrary units)",
           title="Nine sequential MAC updates — synthetic power trace")
    ax.legend(); fig.tight_layout()
    return fig


def plot_candidates(inputs, traces, prefix, index, model="HD"):
    import matplotlib.pyplot as plt
    scores = cpa(inputs, traces, prefix, index, model)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(CANDIDATES, scores, label=model)
    ax.set(xlabel="Signed int8 candidate weight (integer)", ylabel="Pearson r (unitless)",
           title=f"Weight index {index}: correlation across {len(inputs)} executions", ylim=(-1.05, 1.05))
    ax.legend(); fig.tight_layout()
    return fig


class Investigation:
    """A logged teaching budget, not a security boundary on a local machine."""
    def __init__(self, root=None):
        self.root = Path(root) if root else Path(__file__).parent
        self.manifest = json.loads((self.root / "manifest.json").read_text())
        self.known = self.manifest["known_first_weight"]
        self.inputs = np.empty((0, 9), dtype=np.int64)
        self.traces = np.empty((0, 108))
        self.cursors = {k: 0 for k in ("diverse", "narrow", "repeated")}
        self.ledger = []; self.notes = {}; self.frozen = None; self.validation = None

    def acquire(self, kind, count, prediction):
        if self.frozen is not None:
            raise ValueError("Selection frozen: discovery acquisition is closed.")
        if kind not in self.cursors or count not in (32, 64, 128):
            raise ValueError("Choose diverse/narrow/repeated and 32/64/128 traces.")
        if not isinstance(prediction, str) or len(prediction.strip()) < 10:
            raise ValueError("Record a specific prediction before acquisition.")
        if len(self.inputs) + count > 256:
            raise ValueError("Discovery limit is 256. Reserve 64 of the 320 credits for validation.")
        start = self.cursors[kind]; stop = start + count
        with np.load(self.root / "packets" / f"{kind}.npz", allow_pickle=False) as p:
            if stop > len(p["inputs"]):
                raise ValueError("Packet exhausted.")
            x, t = p["inputs"][start:stop].copy(), p["traces"][start:stop].copy()
        self.inputs = np.concatenate([self.inputs, x])
        self.traces = np.concatenate([self.traces, t])
        self.cursors[kind] = stop
        self.ledger.append({"kind": kind, "start": start, "count": count,
                            "prediction": prediction, "total_discovery": len(self.inputs)})
        return {"acquired": count, "discovery_used": len(self.inputs),
                "credits_left_including_validation": 320-len(self.inputs)}

    def freeze(self, guesses):
        if self.frozen is not None:
            raise ValueError("Already frozen. A revised tuple needs a fresh investigation and validation set.")
        if len(guesses) != 3 or any(type(v) is not int or not -128 <= v <= 127 or v == 0 for v in guesses):
            raise ValueError("Submit three nonzero signed int8 Python integers.")
        if len(self.inputs) < 32:
            raise ValueError("Collect discovery evidence before freezing.")
        self.frozen = list(guesses)

    def load_packet(self, name):
        """Load guided data, or defense data after freezing, as input/trace arrays."""
        allowed = ("guided", "defense_baseline", "defense_storage_encryption", "defense_more_noise")
        if name not in allowed:
            raise ValueError("Use acquire for discovery and open_validation for validation.")
        if name != "guided" and self.frozen is None:
            raise ValueError("Freeze your selections before opening defense packets.")
        with np.load(self.root / "packets" / f"{name}.npz", allow_pickle=False) as p:
            return p["inputs"].copy(), p["traces"].copy()

    def open_validation(self):
        """Return the reserved raw observations once selections are frozen."""
        if self.frozen is None:
            raise ValueError("Freeze three guesses before opening validation.")
        if not hasattr(self, "_validation_data"):
            with np.load(self.root / "packets" / "validation.npz", allow_pickle=False) as p:
                self._validation_data = (p["inputs"].copy(), p["traces"].copy())
            self.ledger.append({"kind": "validation", "count": 64,
                                "total_used": len(self.inputs)+64})
        return tuple(a.copy() for a in self._validation_data)

    def record_validation(self, evidence):
        """Store student-computed validation results; no analysis is performed here."""
        import math
        if not hasattr(self, "_validation_data"):
            raise ValueError("Open validation observations first.")
        if self.validation is not None:
            raise ValueError("Validation results already recorded.")
        if not isinstance(evidence, list) or len(evidence) != 3:
            raise ValueError("Provide one validation dictionary for each target.")
        for j, row in enumerate(evidence, 1):
            if not isinstance(row, dict) or row.get("index") != j or row.get("chosen") != self.frozen[j-1]:
                raise ValueError("Validation must identify each frozen target in order.")
            r, rank = row.get("held_out_r"), row.get("rank")
            if "held_out_r" not in row or "rank" not in row:
                raise ValueError("Each result needs held_out_r and rank.")
            if r is None:
                if rank is not None:
                    raise ValueError("Undefined correlation needs rank=None.")
            elif type(r) not in (int, float) or not math.isfinite(r) or not -1.0000001 <= r <= 1.0000001 or type(rank) is not int or not 1 <= rank <= 256:
                raise ValueError("Use a finite correlation and integer rank, or None for both.")
        self.validation = json.loads(json.dumps(evidence, allow_nan=False))
        return self.validation

    def export(self, path="submission.json"):
        required = ("hd_calculation", "acquisition_observation", "candidate_evidence",
                    "defense", "threat_model", "transfer_answer")
        if self.validation is None or any(not str(self.notes.get(k, "")).strip() for k in required):
            raise ValueError("Validate and complete all six evidence notes before exporting.")
        data = {"instance_id": self.manifest["instance_id"], "guesses": self.frozen,
                "ledger": self.ledger, "validation": self.validation, "notes": self.notes}
        Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")
        return str(Path(path).resolve())


    def rank(self, prefix, model="HD"):
        if not len(self.inputs):
            raise ValueError("Acquire traces first.")
        if len(prefix) not in (1, 2, 3) or prefix[0] != self.known:
            raise ValueError("Start with the known weight and append your own previous guesses.")
        return ranking(self.inputs, self.traces, prefix, len(prefix), model)

    def validate(self):
        if self.validation is not None:
            return self.validation
        inputs, traces = self.open_validation()
        prefix = [self.known]
        evidence = []
        for j, g in enumerate(self.frozen, 1):
            scores = cpa(inputs, traces, prefix, j)
            value = scores[g+128]
            evidence.append({"index": j, "chosen": g,
                             "held_out_r": float(value) if np.isfinite(value) else None,
                             "rank": int(1+np.sum(scores > value)) if np.isfinite(value) else None})
            prefix.append(g)
        return self.record_validation(evidence)
