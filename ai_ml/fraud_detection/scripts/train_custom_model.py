#!/usr/bin/env python3
"""
Train a simple TF-IDF + PyTorch MLP fraud classifier.

Input CSV must contain:
  - text: string (e.g., title + selftext + ocr_text)
  - label: int (1=fraud, 0=legit)

Usage:
  python ai_ml/fraud_detection/scripts/train_custom_model.py --csv data/labeled.csv --out ai_ml/fraud_detection/app/models/custom_model_ckpt
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib

from ai_ml.fraud_detection.app.models.custom_model import MLP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Labeled CSV path with columns: text,label")
    parser.add_argument("--out", required=True, help="Output ckpt dir")
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--max_features", type=int, default=50000)
    args = parser.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv)
    assert "text" in df.columns and "label" in df.columns, "CSV must contain text,label"
    df["text"] = df["text"].fillna("").astype(str)
    df["label"] = df["label"].astype(int)

    X_train, X_val, y_train, y_val = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=0.2,
        random_state=42,
        stratify=df["label"].tolist() if df["label"].nunique() > 1 else None,
    )

    vec = TfidfVectorizer(
        max_features=args.max_features,
        ngram_range=(1, 2),
        min_df=2,
    )
    Xtr = vec.fit_transform(X_train)
    Xva = vec.transform(X_val)

    xtr = torch.from_numpy(Xtr.toarray()).float()
    ytr = torch.tensor(y_train).float()
    xva = torch.from_numpy(Xva.toarray()).float()
    yva = torch.tensor(y_val).float()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = MLP(in_dim=xtr.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    def batch_iter(x, y, bs=64):
        idx = np.arange(len(y))
        np.random.shuffle(idx)
        for i in range(0, len(y), bs):
            j = idx[i:i+bs]
            yield x[j], y[j]

    best_val = 0.0
    for epoch in range(1, args.epochs + 1):
        model.train()
        for xb, yb in batch_iter(xtr, ytr):
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            logits = model(xva.to(device)).cpu()
            probs = torch.sigmoid(logits)
            preds = (probs >= 0.5).long()
            acc = (preds == yva.long()).float().mean().item()
        print(f"epoch={epoch} val_acc={acc:.4f}")
        best_val = max(best_val, acc)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vec, out_dir / "vectorizer.joblib")
    torch.save({"in_dim": xtr.shape[1], "state_dict": model.cpu().state_dict()}, out_dir / "model.pt")
    print(f"Saved to: {out_dir}")
    print(f"Best val_acc: {best_val:.4f}")


if __name__ == "__main__":
    main()
