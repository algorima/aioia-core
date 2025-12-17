from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch

try:
    import joblib  # type: ignore
except Exception:
    joblib = None  # type: ignore


class MLP(torch.nn.Module):
    def __init__(self, in_dim: int, hidden: int = 256, dropout: float = 0.2):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(hidden, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


@dataclass
class CustomModel:
    ckpt_dir: Path
    device: str = "cpu"

    _vectorizer: Optional[object] = None
    _model: Optional[MLP] = None

    def load(self) -> None:
        if self._model is not None and self._vectorizer is not None:
            return
        if joblib is None:
            raise RuntimeError("joblib not installed. Install scikit-learn and joblib.")

        vec_path = self.ckpt_dir / "vectorizer.joblib"
        model_path = self.ckpt_dir / "model.pt"
        if not vec_path.exists() or not model_path.exists():
            return

        self._vectorizer = joblib.load(vec_path)
        payload = torch.load(model_path, map_location="cpu")
        in_dim = int(payload["in_dim"])
        model = MLP(in_dim=in_dim)
        model.load_state_dict(payload["state_dict"])
        model.to(self.device)
        model.eval()
        self._model = model

    @torch.inference_mode()
    def predict_proba(self, text: str) -> Optional[float]:
        self.load()
        if self._model is None or self._vectorizer is None:
            return None

        X = self._vectorizer.transform([text])
        x = torch.from_numpy(X.toarray()).float().to(self.device)
        logit = self._model(x)
        prob = torch.sigmoid(logit).item()
        return float(prob)
