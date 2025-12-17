from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Label = Literal["fraud", "legit", "uncertain"]


class Signal(BaseModel):
    type: str = Field(..., description="Normalized risk signal type")
    evidence: str = Field(..., description="Short evidence span from text/OCR")


class ModelVotes(BaseModel):
    custom_model_prob: Optional[float] = None
    llm_label: Optional[Label] = None
    llm_confidence: Optional[float] = None


class AnalyzeResponse(BaseModel):
    label: Label
    risk_score: float = Field(..., ge=0.0, le=1.0)
    model_votes: ModelVotes
    signals: List[Signal] = Field(default_factory=list)
    summary: str = ""
    debug: Dict[str, Any] = Field(default_factory=dict)
