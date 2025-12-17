from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .settings import settings
from .services.storage import LocalStorage
from .services.preprocess_text import build_llm_bundle, normalize_text, extract_risk_signals
from .services.preprocess_image import load_and_normalize, save_normalized, maybe_ocr_text
from .services.llm_client import LLMClient
from .services.ensemble import decide_label
from .models.custom_model import CustomModel


class FraudPipeline:
    def __init__(self) -> None:
        self.storage = LocalStorage(Path(settings.STORAGE_ROOT))
        self.llm = LLMClient(
            model_name=settings.LLM_MODEL_NAME,
            max_new_tokens=settings.LLM_MAX_NEW_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            use_4bit=settings.LLM_USE_4BIT,
            trust_remote_code=settings.LLM_TRUST_REMOTE_CODE,
        )
        self.custom = CustomModel(
            Path(settings.CUSTOM_MODEL_DIR),
            device="cuda" if Path("/dev/nvidia0").exists() else "cpu",
        )

    def analyze(self, user_text: str = "", image_paths: Optional[List[Path]] = None) -> Dict[str, Any]:
        req_id = uuid.uuid4().hex[:12]
        user_text = normalize_text(user_text or "")

        image_paths = image_paths or []
        processed_paths: List[Path] = []
        ocr_texts: List[str] = []

        for idx, p in enumerate(image_paths):
            try:
                img = load_and_normalize(p)
                out = save_normalized(img, Path(settings.STORAGE_ROOT) / "images" / req_id / f"{idx}.jpg")
                processed_paths.append(out.path)
                ocr_texts.append(maybe_ocr_text(out.path))
            except Exception:
                continue

        ocr_text = "\n".join([t for t in ocr_texts if t]).strip()

        custom_prob = self.custom.predict_proba(user_text + "\n" + ocr_text)

        llm_out = None
        try:
            bundle = build_llm_bundle(user_text, ocr_text)
            llm_out = self.llm.classify(bundle)
        except Exception:
            llm_out = None

        label, risk_score = decide_label(custom_prob, llm_out)

        sigs = extract_risk_signals(user_text + "\n" + ocr_text)
        signals = [{"type": t, "evidence": e} for t, e in sigs]

        summary = ""
        if llm_out and isinstance(llm_out, dict):
            summary = str(llm_out.get("summary", ""))[:1000]

        debug: Dict[str, Any] = {
            "request_id": req_id,
            "processed_images": [str(p) for p in processed_paths],
            "ocr_text": ocr_text[:2000],
        }

        if settings.SAVE_INPUTS:
            self.storage.put_json(f"runs/{req_id}/bundle.json", {
                "user_text": user_text,
                "ocr_text": ocr_text,
                "custom_prob": custom_prob,
                "llm_out": llm_out,
            })

        return {
            "label": label,
            "risk_score": float(max(0.0, min(1.0, risk_score))),
            "model_votes": {
                "custom_model_prob": custom_prob,
                "llm_label": (llm_out or {}).get("label") if llm_out else None,
                "llm_confidence": (llm_out or {}).get("confidence") if llm_out else None,
            },
            "signals": signals,
            "summary": summary,
            "debug": debug,
        }
