# 🎵 K-pop 포토카드 거래 게시글 수집 스크립트

Reddit에서 K-pop 아이돌 포토카드 거래 게시글(WTS/WTB/WTT)을 자동으로 수집하는 스크립트입니다.

## 📁 폴더 구조

```
share/
├── README.md                    # 이 파일 (사용 설명서)
├── collect_kpop_trade.py        # 메인 수집 스크립트
├── requirements.txt             # 필요한 패키지
├── .env.example                 # 환경변수 설정 예시
└── sample_data/
    └── seventeen_trade_sample.jsonl  # 수집 결과 예시
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 열어서 SERPAPI_KEY 입력
```

### 2. SerpAPI 키 발급

1. [https://serpapi.com/](https://serpapi.com/) 가입
2. 무료 플랜: 월 100회 검색 가능
3. API Key 복사 → `.env` 파일에 붙여넣기

### 3. 실행

```bash
# 기본 실행 (세븐틴 포토카드 거래글 수집)
python collect_kpop_trade.py

# 다른 아이돌로 수집
python collect_kpop_trade.py --artist "BTS"
python collect_kpop_trade.py --artist "Stray Kids"
python collect_kpop_trade.py --artist "NewJeans"

# 수집 개수 조정
python collect_kpop_trade.py --limit 50
```

## 📊 수집되는 데이터

### 거래 유형
- **WTS** (Want To Sell) - 팔고 싶어요
- **WTB** (Want To Buy) - 사고 싶어요
- **WTT** (Want To Trade) - 교환해요
- **ISO** (In Search Of) - 찾고 있어요

### 출력 파일 (JSONL 형식)

```json
{
  "url": "https://www.reddit.com/r/kpopforsale/comments/...",
  "title": "[WTS][USA] Seventeen Photocards $3 each",
  "snippet": "All photocards are in mint condition...",
  "source": "reddit",
  "lang": "en",
  "queried_at": "2025-12-10T11:46:35.078504"
}
```

## 🔑 주요 키워드

| 영어 | 의미 | 예시 |
|------|------|------|
| WTS | 판매 | [WTS] Selling SVT PCs |
| WTB | 구매 | [WTB] Looking for Mingyu PC |
| WTT | 교환 | [WTT] Trading Seventeen PCs |
| ISO | 찾음 | ISO Vernon Birthday PC |
| PC | 포토카드 | SVT PC for sale |
| POB | Pre-Order Benefit | FML POB trade |

## ⚠️ 주의사항

1. **API 사용량**: SerpAPI 무료 플랜은 월 100회 제한
2. **Rate Limiting**: 과도한 요청 시 차단될 수 있음
3. **데이터 활용**: 수집한 데이터는 연구/분석 목적으로만 사용

## 💡 활용 아이디어

- 가격 동향 분석: 어떤 멤버 포카가 가장 비싼지?
- 인기 분석: 어떤 앨범/버전이 가장 많이 거래되는지?
- 시장 조사: 거래 게시글 패턴, 지역별 분포 등

## 📞 문의

궁금한 점이 있으면 언제든 물어보세요!

