# Fraud Detection (K-pop trade) — FastAPI + PyTorch + LLM

This module provides an API that accepts:
- Free-form trade text (paste)
- Optional images (screenshots), which can be OCR'd (optional)
Then returns:
- fraud / legit / uncertain
- risk_score (0..1)
- structured signals + short explanation

## Architecture (MVP)
1) Text preprocess (regex, keyword signals)
2) Optional image preprocess + OCR (hook)
3) Custom ML baseline (TF-IDF + PyTorch MLP) -> probability
4) LLM classifier (HF Transformers) -> JSON (label/confidence/signals)
5) Ensemble rule -> final label

## Quickstart (local)
```bash
cd aioia-core
python -m venv .venv
source .venv/bin/activate
pip install -r ai_ml/fraud_detection/requirements.txt

export LLM_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
export LLM_USE_4BIT=0

uvicorn ai_ml.fraud_detection.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test via curl
```bash
curl -X POST "http://localhost:8000/v1/analyze" -F "text=WTS DAY6 ticket. 선입금 부탁드려요."
```

### Test via CLI (no backend knowledge)
```bash
python ai_ml/fraud_detection/scripts/demo_cli.py < sample.txt
python ai_ml/fraud_detection/scripts/demo_cli.py --image /path/a.jpg < sample.txt
```

## RunPod (recommended: use a PyTorch/CUDA template)
```bash
cd /workspace
git clone <your-repo-url>
cd aioia-core
pip install -r ai_ml/fraud_detection/requirements.txt

# 24GB baseline:
export LLM_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
export LLM_USE_4BIT=0

# 48GB option (bigger model, 4bit):
# export LLM_MODEL_NAME="Qwen/Qwen2.5-32B-Instruct"
# export LLM_USE_4BIT=1

uvicorn ai_ml.fraud_detection.app.main:app --host 0.0.0.0 --port 8000
```

## Custom ML baseline training
You need labels.

1) Create silver labels (bootstrap):
```bash
python ai_ml/fraud_detection/scripts/weak_label.py --in /path/kpopforsale.csv --out data/silver.csv
```

2) Create final labeled CSV with columns: `text,label` then train:
```bash
python ai_ml/fraud_detection/scripts/train_custom_model.py --csv data/labeled.csv \
  --out ai_ml/fraud_detection/app/models/custom_model_ckpt
```

## Labeling workflow (recommended)
1) Bootstrap with weak labels (silver):
```bash
python ai_ml/fraud_detection/scripts/weak_label.py --in /path/kpopforsale.csv --out data/silver.csv
```

2) Make a clean labeled set with the interactive CLI:
```bash
python ai_ml/fraud_detection/scripts/label_cli.py --in /path/kpopforsale.csv --out data/labeled_raw.csv
```

3) Convert to strict `text,label` if needed, then train custom baseline:
```bash
python ai_ml/fraud_detection/scripts/train_custom_model.py --csv data/labeled.csv --out ai_ml/fraud_detection/app/models/custom_model_ckpt
```

## SerpAPI key rotation (team keys)
Set:
- `SERPAPI_KEYS="k1,k2,k3,..."`

Then use:
```bash
python ai_ml/fraud_detection/data_collection/collect_kpop_trade_rotating.py \
  --query "site:reddit.com/r/kpopforsale WTS photocard" \
  --out data/new_posts.jsonl
```

## LoRA / QLoRA fine-tuning (PEFT)
Install extra deps:
```bash
pip install -r ai_ml/fraud_detection/requirements-lora.txt
```

Train (example):
```bash
python ai_ml/fraud_detection/scripts/train_lora.py \
  --base_model Qwen/Qwen2.5-7B-Instruct \
  --train_csv data/labeled.csv \
  --out_dir outputs/lora_qwen7b \
  --use_4bit 1
```
