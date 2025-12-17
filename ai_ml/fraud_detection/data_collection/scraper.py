#!/usr/bin/env python3
"""
Reddit r/kpopforsale 스크래퍼 (JSON API 버전)
- r/<subreddit>의 게시글을 수집하여 kpopforsale.csv 스키마로 CSV 저장
- SerpAPI 키 불필요 (Reddit JSON을 직접 호출)
"""

import argparse
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
import pandas as pd


class KpopForSaleScraper:
    """r/kpopforsale 서브레딧 스크래퍼 (Reddit JSON API 사용)"""

    BASE_URL = "https://www.reddit.com/r/kpopforsale.json"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    def __init__(
        self,
        delay: float = 2.0,
        base_url: Optional[str] = None,
        include_stickied: bool = False,
        selftext_max: int = 500,
    ):
        """
        Args:
            delay: 요청 간 지연 시간 (초)
            base_url: 기본 URL override (예: https://www.reddit.com/r/kpopforsale/new.json)
            include_stickied: 공지(stickied) 포함 여부
            selftext_max: selftext를 저장할 최대 글자 수 (0이면 전체 저장)
        """
        self.delay = float(delay)
        self.include_stickied = bool(include_stickied)
        self.selftext_max = int(selftext_max)

        if base_url:
            self.BASE_URL = base_url

        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _fetch_json(self, url: str) -> Optional[dict]:
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"[ERROR] JSON 요청 실패: {url} - {e}")
            return None
        except ValueError as e:
            print(f"[ERROR] JSON 파싱 실패: {e}")
            return None

    def _extract_image_url(self, data: dict) -> str:
        media_metadata = data.get("media_metadata", {})
        if media_metadata:
            for _, media_info in media_metadata.items():
                if media_info.get("status") == "valid":
                    source = media_info.get("s", {})
                    if source.get("u"):
                        return source["u"].replace("&amp;", "&")

        url = data.get("url_overridden_by_dest", "") or data.get("url", "")
        if url and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            return url

        preview = data.get("preview", {})
        images = preview.get("images", [])
        if images:
            source = images[0].get("source", {})
            if source.get("url"):
                return source["url"].replace("&amp;", "&")

        return ""

    def _parse_transaction_type(self, title: str) -> str:
        title_upper = title.upper()
        types = []
        if "[WTS]" in title_upper or "WTS" in title_upper:
            types.append("WTS")
        if "[WTB]" in title_upper or "WTB" in title_upper:
            types.append("WTB")
        if "[WTT]" in title_upper or "WTT" in title_upper:
            types.append("WTT")
        if "[GIVEAWAY]" in title_upper or "GIVEAWAY" in title_upper:
            types.append("GIVEAWAY")
        if "PRICE CHECK" in title_upper:
            types.append("PRICE CHECK")
        return "/".join(types) if types else "OTHER"

    def _parse_country(self, title: str) -> str:
        matches = re.findall(r"\[([A-Z]{2,3})\]", title.upper())
        exclude = {"WTS", "WTB", "WTT", "WW"}
        for m in matches:
            if m not in exclude:
                return m
        if "WW" in matches or "[WW]" in title.upper():
            return "WW"
        return ""

    def _parse_post(self, post_data: dict) -> Optional[dict]:
        try:
            data = post_data.get("data", {})

            post_id = data.get("id", "")
            title = data.get("title", "")
            author = data.get("author", "")
            permalink = data.get("permalink", "")
            created_utc = data.get("created_utc", 0)
            score = data.get("score", 0)
            comment_count = data.get("num_comments", 0)
            selftext = data.get("selftext", "")

            full_url = f"https://www.reddit.com{permalink}" if permalink else ""

            flair = data.get("link_flair_text", "") or ""
            author_flair = data.get("author_flair_text", "") or ""

            first_image_url = self._extract_image_url(data)
            transaction_type = self._parse_transaction_type(title)
            country = self._parse_country(title)

            created_timestamp = ""
            if created_utc:
                created_timestamp = datetime.utcfromtimestamp(created_utc).isoformat()

            if self.selftext_max and self.selftext_max > 0:
                st = selftext[: self.selftext_max] if selftext else ""
            else:
                st = selftext or ""

            return {
                "post_id": post_id,
                "title": title,
                "author": author,
                "author_flair": author_flair,
                "transaction_type": transaction_type,
                "country": country,
                "flair": flair,
                "score": score,
                "comment_count": comment_count,
                "selftext": st,
                "created_timestamp": created_timestamp,
                "permalink": full_url,
                "first_image_url": first_image_url,
                "is_gallery": data.get("is_gallery", False),
                "scraped_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"[ERROR] 게시글 파싱 실패: {e}")
            return None

    def scrape(self, max_posts: int = 1000) -> list[dict]:
        print(f"[INFO] 스크래핑 시작: {self.BASE_URL} (최대 {max_posts}개)")

        posts: list[dict] = []
        after = None
        page = 0

        while len(posts) < max_posts:
            page += 1
            url = self.BASE_URL
            if after:
                joiner = "&" if "?" in url else "?"
                url += f"{joiner}after={after}"

            print(f"[INFO] 페이지 {page} 요청 중... (현재: {len(posts)}개)")
            json_data = self._fetch_json(url)
            if not json_data:
                break

            listing = json_data.get("data", {})
            children = listing.get("children", [])
            if not children:
                print("[INFO] 더 이상 게시글이 없습니다.")
                break

            for child in children:
                if len(posts) >= max_posts:
                    break

                if (not self.include_stickied) and child.get("data", {}).get("stickied", False):
                    continue

                post_data = self._parse_post(child)
                if post_data:
                    posts.append(post_data)
                    title_preview = (post_data.get("title") or "")[:50]
                    print(f"  [{len(posts)}] {title_preview}...")

            after = listing.get("after")
            if not after:
                print("[INFO] 마지막 페이지입니다.")
                break

            if self.delay > 0:
                time.sleep(self.delay)

        print(f"[INFO] 스크래핑 완료: 총 {len(posts)}개 게시글 수집")
        return posts

    def save_to_csv(self, posts: list[dict], filename: str):
        if not posts:
            print("[WARN] 저장할 데이터가 없습니다.")
            return

        df = pd.DataFrame(posts)

        column_order = [
            "post_id", "title", "author", "author_flair",
            "transaction_type", "country", "flair",
            "score", "comment_count", "selftext",
            "created_timestamp", "permalink", "first_image_url",
            "is_gallery", "scraped_at",
        ]

        existing_cols = [c for c in column_order if c in df.columns]
        df = df[existing_cols]

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"[INFO] CSV 저장 완료: {Path(filename).resolve()}")


def _default_out_path(subreddit: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return str(Path("data") / f"{subreddit}_{ts}.csv")


def main():
    ap = argparse.ArgumentParser(description="Scrape Reddit JSON (subreddit listing) and save to CSV")
    ap.add_argument("--subreddit", default="kpopforsale", help="Subreddit name (default: kpopforsale)")
    ap.add_argument("--sort", choices=["new", "hot"], default="new", help="Listing sort (new/hot)")
    ap.add_argument("--max-posts", type=int, default=1000, help="Max posts to collect")
    ap.add_argument("--delay", type=float, default=2.0, help="Delay seconds between requests")
    ap.add_argument("--out", type=str, default="", help="Output CSV path (default: data/<subreddit>_YYYYMMDD_HHMM.csv)")
    ap.add_argument("--include-stickied", action="store_true", help="Include stickied posts")
    ap.add_argument("--selftext-max", type=int, default=500, help="Max chars of selftext to store (0 = full)")
    ap.add_argument("--no-summary", action="store_true", help="Disable summary print")
    args = ap.parse_args()

    subreddit = args.subreddit.strip().lstrip("r/").strip("/")
    if args.sort == "new":
        base_url = f"https://www.reddit.com/r/{subreddit}/new.json"
    else:
        base_url = f"https://www.reddit.com/r/{subreddit}.json"

    out_path = args.out or _default_out_path(subreddit)

    scraper = KpopForSaleScraper(
        delay=args.delay,
        base_url=base_url,
        include_stickied=args.include_stickied,
        selftext_max=args.selftext_max,
    )
    posts = scraper.scrape(max_posts=args.max_posts)
    scraper.save_to_csv(posts, out_path)

    if (not args.no_summary) and posts:
        df = pd.DataFrame(posts)
        print("\n=== Summary ===")
        print(f"총 게시글: {len(posts)}")
        if "transaction_type" in df.columns:
            print("\n거래 유형 분포:\n" + df["transaction_type"].value_counts().to_string())
        if "country" in df.columns:
            print("\n국가 분포(상위 10):\n" + df["country"].value_counts().head(10).to_string())
        if "first_image_url" in df.columns:
            has_image = df["first_image_url"].apply(lambda x: bool(x)).sum()
            print(f"\n이미지 포함 게시글: {has_image}개 ({has_image/len(posts)*100:.1f}%)")


if __name__ == "__main__":
    main()
