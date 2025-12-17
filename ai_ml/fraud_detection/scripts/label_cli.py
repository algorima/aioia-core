#!/usr/bin/env python3
"""
Interactive labeling CLI (fraud/legit/uncertain) for trade posts.

Keys:
  f = fraud (label=1)
  l = legit (label=0)
  u = uncertain (label=-1)
  s = skip
  q = quit

Usage:
  python ai_ml/fraud_detection/scripts/label_cli.py --in /path/kpopforsale.csv --out data/labeled.csv
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

LABEL_MAP = {"f": 1, "l": 0, "u": -1}


def build_text(row: pd.Series) -> str:
    title = str(row.get("title", "") or "")
    body = str(row.get("selftext", "") or "")
    return (title + "\n" + body).strip()


def _append(out_path: Path, rows: list[dict]):
    df_new = pd.DataFrame(rows)
    if out_path.exists():
        df_old = pd.read_csv(out_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        df_all.to_csv(out_path, index=False)
    else:
        df_new.to_csv(out_path, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=0)
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    done_ids = set()
    if out_path.exists():
        prev = pd.read_csv(out_path)
        if "post_id" in prev.columns:
            done_ids = set(prev["post_id"].astype(str).tolist())

    buf: list[dict] = []
    total = len(df)

    for i in range(args.start, total):
        row = df.iloc[i]
        post_id = str(row.get("post_id", i))
        if post_id in done_ids:
            continue

        text = build_text(row)
        permalink = str(row.get("permalink", "") or "")
        img = str(row.get("first_image_url", "") or "")

        os.system("cls" if os.name == "nt" else "clear")
        print(f"[{i+1}/{total}] post_id={post_id}")
        if permalink:
            print(f"permalink: {permalink}")
        if img:
            print(f"image:     {img}")
        print("-" * 80)
        print(text[:4000])
        print("-" * 80)

        while True:
            key = input("Label? [f]raud/[l]egit/[u]ncertain/[s]kip/[q]quit > ").strip().lower()
            if key == "q":
                if buf:
                    _append(out_path, buf)
                print("Quit.")
                return
            if key == "s":
                break
            if key in LABEL_MAP:
                label = LABEL_MAP[key]
                buf.append({
                    "post_id": post_id,
                    "label": label,
                    "text": text,
                    "permalink": permalink,
                    "first_image_url": img,
                })
                if len(buf) >= 20:
                    _append(out_path, buf)
                    buf = []
                break
            print("Invalid key. Use f/l/u/s/q.")

    if buf:
        _append(out_path, buf)
    print(f"Done. Saved -> {out_path}")


if __name__ == "__main__":
    main()
