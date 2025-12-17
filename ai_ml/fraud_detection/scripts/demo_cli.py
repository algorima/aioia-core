#!/usr/bin/env python3
"""
Quick local test without any backend knowledge.

Usage:
  python ai_ml/fraud_detection/scripts/demo_cli.py < sample.txt
  python ai_ml/fraud_detection/scripts/demo_cli.py --image /path/to/img.jpg < sample.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_ml.fraud_detection.app.pipeline import FraudPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", action="append", default=[], help="Image path (repeatable)")
    args = parser.parse_args()

    print("Paste trade text, then finish input:")
    text = sys.stdin.read()

    image_paths = [Path(p) for p in args.image]
    pipe = FraudPipeline()
    out = pipe.analyze(user_text=text, image_paths=image_paths)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
