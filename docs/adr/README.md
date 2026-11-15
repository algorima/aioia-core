# ADR (Architecture Decision Record)

공개 API나 패키지 구조처럼 **이후 코드가 계속 따라야 하는 기술 선택 하나**를 남기는 곳입니다.
결정의 배경이 PR 설명에만 남으면 머지 뒤에 찾기 어렵기 때문입니다.

## 언제 쓰나

다음 중 하나라면 ADR을 씁니다.

- 하위 호환을 깨는 변경을 한다 (`feat(python)!:` 처럼 `!`가 붙는 커밋)
- 공개 API의 형태나 규약을 정한다 (예: 목록 쿼리 키, 에러 처리 방식, DI 지점)
- 의존성을 더하거나 뺀다 (`CLAUDE.md`의 "최소 의존성"에 영향을 주는 경우)
- Python과 TypeScript 패키지가 같이 따라야 하는 규칙을 정한다

버그 수정, 내부 리팩토링, 기존 ADR을 그대로 따르는 변경에는 쓰지 않습니다.

## 파일명

```
docs/adr/ADR-{4자리 번호}-{slug}.md
```

- 번호는 `docs/adr/`에서 가장 큰 번호 + 1입니다. 두 PR이 같은 번호를 잡으면 나중에 머지하는 쪽이 번호를 바꿉니다.
- frontmatter `id`는 파일명 번호와 같아야 합니다.
- 아래 "템플릿"을 복사해서 시작합니다.

## 상태와 불변

- `status`는 `Accepted` 또는 `Superseded by ADR-{번호}` 둘뿐입니다. 검토 중인 상태는 PR이 표현합니다.
- 머지된 ADR은 `status`와 `scope`만 고칠 수 있습니다.
- 결정을 바꾸려면 새 ADR을 쓰고 `supersedes`에 옛 id를 적은 뒤, 옛 ADR의 `status`를 `Superseded by {새 id}`로 바꿉니다.

이 규칙은 아직 CI로 검사하지 않습니다. 리뷰에서 확인합니다.

## 템플릿

```markdown
---
id: ADR-{번호}
status: Accepted
date: YYYY-MM-DD
scope:
  - {이 결정이 적용되는 경로}
supersedes: []
---

# ADR-{번호}: {결정 제목}

## Context

이 결정이 필요했던 배경. 어떤 문제와 제약이 있었는가.

## 후보

검토한 선택지와 각각의 장단점.

## Decision

무엇을 선택했는가. 한두 문장.

## Rationale

왜 다른 후보가 아니라 이것인가.

## Consequences

이 결정으로 생기는 장점, 제약, 이후 코드가 따라야 할 규칙. 하위 호환을 깨면 사용자가 해야 할 마이그레이션도 적는다.

## 재검토 조건

어떤 상황이 되면 이 결정을 다시 볼 것인가.
```
