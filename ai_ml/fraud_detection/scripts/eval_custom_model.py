#!/usr/bin/env python3
"""
Evaluate custom model on labeled CSV.

Usage:
  python ai_ml/fraud_detection/scripts/eval_custom_model.py --csv data/labeled.csv --ckpt ai_ml/fraud_detection/app/models/custom_model_ckpt
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
import joblib
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score

from ai_ml.fraud_detection.app.models.custom_model import MLP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--ckpt", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    assert "text" in df.columns and "label" in df.columns
    texts = df["text"].fillna("").astype(str).tolist()
    y = df["label"].astype(int).to_numpy()

    ckpt = Path(args.ckpt)
    vec = joblib.load(ckpt / "vectorizer.joblib")
    payload = torch.load(ckpt / "model.pt", map_location="cpu")
    model = MLP(in_dim=int(payload["in_dim"]))
    model.load_state_dict(payload["state_dict"])
    model.eval()

    X = vec.transform(texts)
    x = torch.from_numpy(X.toarray()).float()
    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits).numpy()

    pred = (probs >= 0.5).astype(int)
    print(classification_report(y, pred, digits=4))
    try:
        print("ROC-AUC:", roc_auc_score(y, probs))
        print("PR-AUC:", average_precision_score(y, probs))
    except Exception as e:
        print("AUC metrics failed:", e)


if __name__ == "__main__":
    main()
