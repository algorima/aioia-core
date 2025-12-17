#!/usr/bin/env python3
"""
Create silver labels from scraped posts using simple heuristics.
This is NOT ground truth; use to bootstrap, then manually verify.

Usage:
  python ai_ml/fraud_detection/scripts/weak_label.py --in kpopforsale.csv --out data/silver.csv
"""
from __future__ import annotations

import argparse
import pandas as pd

from ai_ml.fraud_detection.app.services.preprocess_text import normalize_text, extract_risk_signals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.inp)
    df["text"] = (df["title"].fillna("") + "\n" + df["selftext"].fillna("")).astype(str)
    df["text_norm"] = df["text"].map(normalize_text)

    def silver_label(t: str) -> int:
        sigs = extract_risk_signals(t)
        sig_types = {s[0] for s in sigs}
        if ("prepayment" in sig_types) or ("move_off_platform" in sig_types) or ("suspicious_link" in sig_types):
            return 1
        return 0

    df["silver_label"] = df["text_norm"].map(silver_label)
    df.to_csv(args.out, index=False)
    print(f"Saved: {args.out} (silver labels only; please manually verify!)")


if __name__ == "__main__":
    main()
