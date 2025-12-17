from __future__ import annotations

from typing import Any, Dict, Tuple

from ..settings import settings


def decide_label(custom_prob: float | None, llm: Dict[str, Any] | None) -> Tuple[str, float]:
    if custom_prob is None:
        custom_prob = 0.5

    if custom_prob >= settings.CUSTOM_MODEL_THRESHOLD_HIGH:
        return "fraud", float(custom_prob)
    if custom_prob <= settings.CUSTOM_MODEL_THRESHOLD_LOW:
        return "legit", float(custom_prob)

    if llm:
        llm_label = str(llm.get("label", "uncertain"))
        llm_conf = float(llm.get("confidence", 0.5) or 0.5)
        if llm_label in {"fraud", "legit"}:
            risk = float((custom_prob + (llm_conf if llm_label == "fraud" else (1.0 - llm_conf))) / 2.0)
            return llm_label, risk

    return "uncertain", float(custom_prob)
