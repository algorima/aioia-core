# AIoIA Core 기여 가이드

## 개발 환경 설정

### Python

```bash
cd python
poetry install
poetry run pytest
poetry run mypy aioia_core
poetry run pylint aioia_core
```

### TypeScript

```bash
cd typescript
npm install
npm test
npm run type-check
```

## 코딩 표준

- **Python**: PEP 8 준수, 타입 힌트 사용
- **TypeScript**: Strict 모드, 명시적 타입
- **테스트**: 새 기능에 테스트 작성
- **문서화**: Docstring과 README 업데이트

## Pull Request

1. `main`에서 feature 브랜치 생성
2. 테스트 작성
3. 모든 검사 통과 확인
4. 명확한 설명과 함께 PR 제출

## 라이선스

Apache 2.0 - LICENSE 파일 참고
