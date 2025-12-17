#!/usr/bin/env python3
"""
Collect candidate K-pop trade posts using SerpAPI with key rotation.

Env:
  SERPAPI_KEYS="k1,k2,k3"   (recommended for your 10 keys)
  or SERPAPI_KEY="single"

Usage:
  python ai_ml/fraud_detection/data_collection/collect_kpop_trade_rotating.py \
    --query "site:reddit.com/r/kpopforsale WTS photocard" \
    --out data/new_posts.jsonl
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .serpapi_rotator import SerpApiRotator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="SerpAPI query string")
    ap.add_argument("--out", required=True, help="Output JSONL path")
    ap.add_argument("--num", type=int, default=100, help="Number of results (<=100 per SerpAPI call)")
    ap.add_argument("--hl", default="en", help="hl param")
    ap.add_argument("--gl", default="us", help="gl param")
    ap.add_argument("--tbs", default="qdr:m6", help="time filter; default recent 6 months")
    args = ap.parse_args()

    rot = SerpApiRotator()

    params = {
        "q": args.query,
        "num": min(args.num, 100),
        "hl": args.hl,
        "gl": args.gl,
        "tbs": args.tbs,
    }
    data = rot.search(params)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    fetched_at = datetime.now().isoformat()
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for item in data.get("organic_results", []) or []:
            rec = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position"),
                "fetched_at": fetched_at,
                "query": args.query,
                "source": "serpapi",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1

    print(f"Saved {n} rows -> {out}")


if __name__ == "__main__":
    main()
