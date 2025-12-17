from __future__ import annotations

import re
from typing import Dict, List, Tuple

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
PHONE_RE = re.compile(r"(?:(?:\+?82|0)\s?-?\s?1[0-9]\s?-?\s?\d{3,4}\s?-?\s?\d{4})|(\b\d{3}[- ]?\d{3,4}[- ]?\d{4}\b)")
ACCOUNT_RE = re.compile(r"\b\d{2,4}[- ]?\d{2,4}[- ]?\d{2,6}[- ]?\d{1,6}\b")

RISK_KEYWORDS = {
    "prepayment": ["선입금", "먼저 입금", "입금 먼저", "prepay", "pre-payment", "zelle", "cashapp", "venmo", "pay first"],
    "urgent_sale": ["급처", "오늘만", "빨리", "urgent", "asap", "need gone", "need these pcs gone"],
    "no_refund": ["환불 불가", "환불x", "no refund", "refund x", "노리턴", "취소 불가"],
    "move_off_platform": ["카톡", "오픈채팅", "openchat", "dm me", "텔레그램", "telegram", "line id"],
    "suspicious_link": ["bit.ly", "tinyurl", "t.co/"],
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def extract_patterns(text: str) -> Dict[str, List[str]]:
    urls = URL_RE.findall(text)
    emails = EMAIL_RE.findall(text)
    phones = [m.group(0) for m in PHONE_RE.finditer(text)]
    accounts = [m.group(0) for m in ACCOUNT_RE.finditer(text)]
    return {
        "urls": list(dict.fromkeys(urls)),
        "emails": list(dict.fromkeys(emails)),
        "phones": list(dict.fromkeys(phones)),
        "accounts": list(dict.fromkeys(accounts)),
    }


def extract_risk_signals(text: str) -> List[Tuple[str, str]]:
    if not text:
        return []
    text_l = text.lower()
    signals: List[Tuple[str, str]] = []
    for sig_type, kws in RISK_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in text_l:
                signals.append((sig_type, kw))
                break
    return signals


def build_llm_bundle(user_text: str, ocr_text: str) -> Dict[str, str]:
    user_text = normalize_text(user_text)
    ocr_text = normalize_text(ocr_text)

    patterns = extract_patterns(user_text + "\n" + ocr_text)
    signals = extract_risk_signals(user_text + "\n" + ocr_text)

    return {
        "user_text": user_text,
        "ocr_text": ocr_text,
        "urls": ", ".join(patterns["urls"][:10]),
        "phones": ", ".join(patterns["phones"][:10]),
        "accounts": ", ".join(patterns["accounts"][:10]),
        "signals": ", ".join([f"{t}:{e}" for t, e in signals[:20]]),
    }
