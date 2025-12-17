from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from .schemas import AnalyzeResponse
from ..pipeline import FraudPipeline

router = APIRouter()
pipeline = FraudPipeline()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/v1/analyze", response_model=AnalyzeResponse)
async def analyze(
    text: Optional[str] = Form(default=""),
    images: Optional[List[UploadFile]] = File(default=None),
):
    tmp_paths: List[Path] = []
    if images:
        for f in images:
            suffix = Path(f.filename or "upload").suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await f.read())
                tmp_paths.append(Path(tmp.name))

    out = pipeline.analyze(user_text=text or "", image_paths=tmp_paths)

    for p in tmp_paths:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass

    return JSONResponse(out)
