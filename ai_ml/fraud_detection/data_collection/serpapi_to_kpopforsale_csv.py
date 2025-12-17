#!/usr/bin/env python3
"""
SerpAPI 결과(JSONL)의 link/url을 따라가서 Reddit 게시글 JSON을 다시 가져오고,
kpopforsale.csv 컬럼 스키마로 CSV를 만든다.

- 입력: SerpAPI JSONL (각 줄에 최소 link/url, title, snippet 등을 가진 dict)
- 출력: kpopforsale.csv 스키마 기반 CSV
- SerpAPI 키는 "검색"할 때만 필요. 이 스크립트는 "링크 따라가기/후처리" 단계라 키가 필요 없다.
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import requests

try:
    from .scraper import KpopForSaleScraper
except Exception:
    from ai_ml.fraud_detection.data_collection.scraper import KpopForSaleScraper


_REDDIT_ID_PATTERNS = [
    re.compile(r"reddit\.com/r/[^/]+/comments/([a-z0-9]+)/", re.IGNORECASE),
    re.compile(r"reddit\.com/comments/([a-z0-9]+)/", re.IGNORECASE),
    re.compile(r"redd\.it/([a-z0-9]+)", re.IGNORECASE),
]


def _extract_reddit_post_id(url: str) -> Optional[str]:
    if not url:
        return None
    for pat in _REDDIT_ID_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    return None


def _fetch_by_id(session: requests.Session, post_id: str) -> Optional[dict]:
    url = f"https://www.reddit.com/by_id/t3_{post_id}.json?raw_json=1"
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _fetch_comments_json(session: requests.Session, post_id: str) -> Optional[list]:
    url = f"https://www.reddit.com/comments/{post_id}.json?raw_json=1"
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _listing_to_child(listing_json: dict) -> Optional[dict]:
    children = (listing_json or {}).get("data", {}).get("children", [])
    return children[0] if children else None


def _comments_to_child(comments_json: list) -> Optional[dict]:
    try:
        return _listing_to_child(comments_json[0])
    except Exception:
        return None


def iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def main():
    ap = argparse.ArgumentParser(description="Convert SerpAPI JSONL links to kpopforsale CSV via Reddit JSON")
    ap.add_argument("--in", dest="in_path", required=True, help="Input JSONL (SerpAPI results)")
    ap.add_argument("--out", dest="out_path", default="", help="Output CSV path (default: data/kpopforsale_from_serpapi_<ts>.csv)")
    ap.add_argument("--max-links", type=int, default=2000, help="Max links to process")
    ap.add_argument("--delay", type=float, default=1.0, help="Delay seconds between Reddit fetches")
    ap.add_argument("--skip-non-reddit", action="store_true", help="Skip non-Reddit links")
    ap.add_argument("--skipped-jsonl", default="", help="Where to save skipped/failed rows (jsonl). default: data/serpapi_skipped_<ts>.jsonl")
    args = ap.parse_args()

    in_path = Path(args.in_path)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    ts = time.strftime("%Y%m%d_%H%M")
    out_path = Path(args.out_path) if args.out_path else Path("data") / f"kpopforsale_from_serpapi_{ts}.csv"
    skipped_path = Path(args.skipped_jsonl) if args.skipped_jsonl else Path("data") / f"serpapi_skipped_{ts}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    skipped_path.parent.mkdir(parents=True, exist_ok=True)

    scraper = KpopForSaleScraper(delay=0.0)
    session = scraper.session

    rows: List[dict] = []
    seen = set()

    processed = 0
    with skipped_path.open("w", encoding="utf-8") as sf:
        for rec in iter_jsonl(in_path):
            if processed >= args.max_links:
                break

            url = rec.get("link") or rec.get("url") or rec.get("permalink") or ""
            post_id = _extract_reddit_post_id(url)

            if not post_id:
                if args.skip_non_reddit:
                    sf.write(json.dumps({**rec, "_skip_reason": "non_reddit_or_no_post_id"}, ensure_ascii=False) + "\n")
                    continue
                sf.write(json.dumps({**rec, "_skip_reason": "no_post_id"}, ensure_ascii=False) + "\n")
                continue

            if post_id in seen:
                continue

            listing = _fetch_by_id(session, post_id)
            child = _listing_to_child(listing) if listing else None

            if child is None:
                comments_json = _fetch_comments_json(session, post_id)
                child = _comments_to_child(comments_json) if comments_json else None

            if child is None:
                sf.write(json.dumps({**rec, "_skip_reason": "reddit_fetch_failed", "_post_id": post_id}, ensure_ascii=False) + "\n")
                continue

            parsed = scraper._parse_post(child)
            if not parsed:
                sf.write(json.dumps({**rec, "_skip_reason": "parse_failed", "_post_id": post_id}, ensure_ascii=False) + "\n")
                continue

            parsed["_serpapi_link"] = url
            parsed["_serpapi_title"] = rec.get("title", "")
            parsed["_serpapi_snippet"] = rec.get("snippet", "")

            rows.append(parsed)
            seen.add(post_id)
            processed += 1

            if args.delay > 0:
                time.sleep(args.delay)

    if not rows:
        print("[WARN] 변환된 row가 없습니다. (입력 JSONL의 link/url이 Reddit 게시글이 맞는지 확인)")
        print(f"[INFO] skipped log: {skipped_path.resolve()}")
        return

    df = pd.DataFrame(rows)

    base_cols = [
        "post_id", "title", "author", "author_flair",
        "transaction_type", "country", "flair",
        "score", "comment_count", "selftext",
        "created_timestamp", "permalink", "first_image_url",
        "is_gallery", "scraped_at",
    ]
    extra_cols = [c for c in df.columns if c not in base_cols]
    df = df[[c for c in base_cols if c in df.columns] + extra_cols]

    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[DONE] rows={len(df)}  saved={out_path.resolve()}")
    print(f"[INFO] skipped log: {skipped_path.resolve()}")


if __name__ == "__main__":
    main()
