# Data Collection (K-pop trade posts)

이 폴더는 K-pop 거래 글(예: r/kpopforsale)을 수집해서
모델 학습/라벨링에 쓰기 좋은 형태(JSONL/CSV)로 저장합니다.

## 어떤 방식으로 수집할까? (추천 가이드)

### A) Reddit JSON 스크래퍼 (추천: r/kpopforsale 전용, 컬럼 완전)
- 장점: `kpopforsale.csv`와 같은 **정형 컬럼**(post_id, title, author, author_flair, score, comment_count, selftext, image_url 등)을 안정적으로 채울 수 있음
- 단점: Reddit 측 rate-limit/차단 가능 → delay 필요

**이걸 쓰면 SerpAPI 키가 필요 없습니다.**

### B) SerpAPI 수집 (추천: 멀티 소스/검색 기반 수집)
- 장점: 구글 검색 기반으로 Reddit/웹/기타 소스까지 확장 가능, 팀원 키 로테이션 가능
- 단점: 결과가 보통 `title/link/snippet` 중심이라 `kpopforsale.csv` 포맷으로 맞추려면 **후처리/추가 크롤링**이 필요할 수 있음(바로 동일 컬럼이 안 나오는 경우 많음)

---

## 설치
프로젝트 루트에서:
```bash
pip install -r ai_ml/fraud_detection/requirements.txt
