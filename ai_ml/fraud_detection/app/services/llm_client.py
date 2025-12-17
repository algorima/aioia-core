from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from transformers import BitsAndBytesConfig
except Exception:
    BitsAndBytesConfig = None  # type: ignore

JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> Dict[str, Any]:
    m = JSON_OBJ_RE.search(text)
    if not m:
        raise ValueError("No JSON object found in LLM output")
    return json.loads(m.group(0))


def build_prompt(bundle: Dict[str, str]) -> str:
    schema = {
        "label": "fraud|legit|uncertain",
        "confidence": "float 0..1",
        "signals": [{"type": "string", "evidence": "string"}],
        "summary": "string (<= 3 sentences)",
    }

    prompt = f"""
너는 K-POP 굿즈/티켓 거래 글의 사기(fraud) 가능성을 평가하는 분류기야.
반드시 아래 JSON 스키마를 따르는 JSON만 출력해. 다른 텍스트는 절대 출력하지 마.

JSON 스키마 예시:
{json.dumps(schema, ensure_ascii=False, indent=2)}

입력(사용자 텍스트):
{bundle.get("user_text","")}

입력(OCR 텍스트, 이미지에서 추출; 없을 수 있음):
{bundle.get("ocr_text","")}

추출된 힌트:
- urls: {bundle.get("urls","")}
- phones: {bundle.get("phones","")}
- accounts: {bundle.get("accounts","")}
- signals: {bundle.get("signals","")}

판정 기준:
- 명확한 사기 징후면 label=fraud
- 정상 거래로 보이면 label=legit
- 정보가 부족하거나 애매하면 label=uncertain
""".strip()
    return prompt


@dataclass
class LLMClient:
    model_name: str
    max_new_tokens: int = 512
    temperature: float = 0.2
    use_4bit: bool = False
    trust_remote_code: bool = True

    _tokenizer: Optional[Any] = None
    _model: Optional[Any] = None

    def load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        quant = None
        if self.use_4bit:
            if BitsAndBytesConfig is None:
                raise RuntimeError("bitsandbytes/transformers BitsAndBytesConfig not available. Install bitsandbytes.")
            quant = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=self.trust_remote_code)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype="auto",
            quantization_config=quant,
            trust_remote_code=self.trust_remote_code,
        )
        self._model.eval()

    @torch.inference_mode()
    def classify(self, bundle: Dict[str, str]) -> Dict[str, Any]:
        self.load()
        prompt = build_prompt(bundle)

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        out = self._model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=self.temperature > 0,
            temperature=self.temperature,
        )
        decoded = self._tokenizer.decode(out[0], skip_special_tokens=True)
        parsed = _extract_json(decoded)

        label = str(parsed.get("label", "uncertain")).lower().strip()
        if label not in {"fraud", "legit", "uncertain"}:
            label = "uncertain"
        parsed["label"] = label
        return parsed
