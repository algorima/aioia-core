When performing a code review, respond in Korean.

# AIoIA Core 개발 가이드

## 코드 품질

- DRY: 공통 패턴 중복 금지
- 제네릭: 타입 안정성 유지
- 최소 의존성: 필수 패키지만 포함
- Guard Clause: 함수 초반에 전제조건 검사, 실패 시 즉시 반환

## 보안

- SQL Injection: ORM 사용
- API 키: 환경 변수 관리
- 타입 검증: Pydantic, Zod

## 테스트

- TDD: Red → Green → Refactor
- 모든 public API 테스트 커버리지

## Python

- SQLAlchemy Enum: `name="snake_case"` 명시
- Tests: `assert <var> is not None` 로 타입 안정성 유지

## 네이밍

- Python: `snake_case.py`, `PascalCase`, `snake_case()`
- TypeScript: `PascalCase.ts`, `camelCase()`, `index.ts`

## 외부 기여

- Atomic PR: 하나의 PR은 하나의 논리적 변경만 포함
- 최소 변경: 안정성 최우선
- 하위 호환성: Breaking change 최소화
- 테스트 필수: 모든 PR에 테스트 포함
