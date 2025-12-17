#!/usr/bin/env python3
"""
LoRA / QLoRA fine-tuning skeleton (PEFT) for the fraud LLM classifier.

Install:
  pip install -r ai_ml/fraud_detection/requirements-lora.txt

Example:
  python ai_ml/fraud_detection/scripts/train_lora.py \
    --base_model Qwen/Qwen2.5-7B-Instruct \
    --train_csv data/labeled.csv \
    --out_dir outputs/lora_qwen7b \
    --use_4bit 1 \
    --epochs 1
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

try:
    from transformers import BitsAndBytesConfig
except Exception:
    BitsAndBytesConfig = None  # type: ignore


def make_prompt(text: str) -> str:
    return (
        "너는 K-POP 굿즈/티켓 거래 글의 사기(fraud) 가능성을 평가하는 분류기야.\n"
        "반드시 JSON만 출력해.\n\n"
        "입력(사용자 텍스트):\n"
        f"{text}\n\n"
        "출력 JSON 스키마:\n"
        '{"label":"fraud|legit|uncertain","confidence":0.0,"signals":[{"type":"string","evidence":"string"}],"summary":"string"}\n'
    )


def label_to_json(label: int) -> str:
    if label == 1:
        return '{"label":"fraud","confidence":0.9,"signals":[],"summary":"fraud"}'
    if label == 0:
        return '{"label":"legit","confidence":0.9,"signals":[],"summary":"legit"}'
    return '{"label":"uncertain","confidence":0.5,"signals":[],"summary":"uncertain"}'


def build_sft_text(row: Dict) -> str:
    prompt = make_prompt(str(row["text"]))
    answer = label_to_json(int(row["label"]))
    return prompt + "\n" + answer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--train_csv", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--use_4bit", type=int, default=1)
    ap.add_argument("--max_seq_len", type=int, default=1024)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--grad_accum", type=int, default=16)
    args = ap.parse_args()

    df = pd.read_csv(args.train_csv)
    assert "text" in df.columns and "label" in df.columns, "train_csv must contain text,label"
    df["text"] = df["text"].fillna("").astype(str)
    df["label"] = df["label"].astype(int)

    sft_texts: List[str] = [build_sft_text(r) for r in df[["text", "label"]].to_dict(orient="records")]
    ds = Dataset.from_dict({"text": sft_texts})

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tok(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_seq_len)

    ds_tok = ds.map(tok, batched=True, remove_columns=["text"])

    quant = None
    if args.use_4bit:
        if BitsAndBytesConfig is None:
            raise RuntimeError("BitsAndBytesConfig not available; install bitsandbytes/transformers.")
        quant = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        device_map="auto",
        torch_dtype="auto",
        quantization_config=quant,
        trust_remote_code=True,
    )

    if args.use_4bit:
        model = prepare_model_for_kbit_training(model)

    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(model, lora)

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(out_dir),
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_steps=200,
        save_total_limit=2,
        bf16=torch.cuda.is_available(),
        fp16=torch.cuda.is_available(),
        report_to=[],
        remove_unused_columns=False,
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=ds_tok, data_collator=collator)
    trainer.train()

    model.save_pretrained(str(out_dir / "lora_adapter"))
    tokenizer.save_pretrained(str(out_dir / "lora_adapter"))
    print(f"Saved LoRA adapter -> {out_dir / 'lora_adapter'}")


if __name__ == "__main__":
    main()
