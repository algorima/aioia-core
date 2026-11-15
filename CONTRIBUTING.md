# AIoIA Core 기여 가이드

## 개발 환경 설정

### Python

```bash
cd python
poetry install
poetry run make test
poetry run make lint
poetry run make type-check
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
4. Conventional Commits 형식으로 커밋
5. 명확한 설명과 함께 PR 제출

## 커밋 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 형식 사용.

**버전 변화**: `feat:`(minor), `fix:`(patch)만 버전 변경. 나머지(`docs:`, `chore:`, `ci:` 등)는 변경 없음.

커밋 타입 전체 목록은 `.github/PULL_REQUEST_TEMPLATE.md` 참조.

## 설계 결정 (ADR)

하위 호환을 깨는 변경, 공개 API 규약, 의존성 추가·제거처럼 이후 코드가 따라야 하는 기술 선택은 [`docs/adr/`](docs/adr/README.md)에 ADR로 남기고, 같은 PR에 포함합니다. 언제 쓰는지와 작성법은 해당 README를 참고하세요.

## 라이선스

Apache 2.0 - LICENSE 파일 참고
