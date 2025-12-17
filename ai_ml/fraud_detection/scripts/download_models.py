#!/usr/bin/env python3
"""
Pre-download HF model weights to warm cache (useful on RunPod).

Usage:
  python ai_ml/fraud_detection/scripts/download_models.py --model "Qwen/Qwen2.5-7B-Instruct"
"""
from __future__ import annotations

import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    AutoModelForCausalLM.from_pretrained(args.model, trust_remote_code=True)
    print("Downloaded:", args.model)


if __name__ == "__main__":
    main()
