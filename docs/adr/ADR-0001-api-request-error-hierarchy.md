---
id: ADR-0001
status: Accepted
date: 2026-11-15
scope:
  - typescript/src/errors/exceptions.ts
  - typescript/src/client/BaseApiService.ts
  - typescript/src/repositories/BaseCrudRepository.ts
supersedes: []
---

# ADR-0001: API 요청 실패를 하나의 예외 계층으로 던진다

## Context

`BaseApiService.request`는 응답이 오지 않은 실패(`fetch` 거부, 본문 읽기 실패)와 응답 본문 파싱 실패를 감싸지 않고 원래 타입(`TypeError`, `SyntaxError`) 그대로 올린다. `BaseCrudRepository.validateResponse`는 응답 스키마 검증 실패를 일반 `Error`로 던진다. HTTP 오류 응답만 하위 클래스의 `handleError`가 `ClientError`·`ServerError`로 바꾼다.

그래서 호출처는 "API가 실패했다"와 "코드에 버그가 있다"를 타입으로 가를 수 없다. `TypeError`는 네트워크 장애일 수도, 코드 버그일 수도 있다. 가를 수 없으니 호출처는 예외를 전부 삼키거나 전부 다시 던지는 둘 중 하나를 고르게 된다. 전부 삼키면 코드 버그가 조용히 묻힌다. buppy의 `fetchPublicCompanions`가 그 예로, 백엔드가 거부한 요청(422)과 코드 버그를 같은 `catch`에서 빈 목록으로 바꿨고, 422는 Sentry에도 남지 않은 채 사이트맵에서 공개 아이돌이 빠졌다(buppy#1542).

응답 본문 `{status, detail, code}`를 `ClientError`·`ServerError`로 바꾸는 코드도 라이브러리에 없어서, 쓰는 쪽(buppy `ServerApiService`의 `readApiError`)이 따로 구현한다.

## 후보

1. **`ApiError`의 `statusCode`를 선택 값으로 바꾸고 `NetworkError`를 `ApiError` 아래에 둔다**
   - 장점: 뿌리가 그대로 `ApiError`라 이름이 하나 준다.
   - 단점: 응답이 없는 오류에 상태 코드 필드가 생겨 타입이 사실과 다르다. `statusCode`를 읽는 모든 코드가 `undefined`를 다뤄야 해서 타입 수준에서 깨진다. `toJSON`의 RFC 9457 `status`도 비게 된다.
2. **`ApiError` 아래에 HTTP 오류용 중간 계층을 새로 둔다**
   - 장점: 뿌리가 `ApiError`로 유지된다.
   - 단점: `ClientError`·`ServerError`의 부모가 바뀌고, `instanceof ApiError`의 뜻이 "HTTP 오류 응답"에서 "모든 요청 실패"로 넓어진다. 지금 `ApiError`를 HTTP 오류로 읽는 코드의 뜻이 조용히 바뀐다.
3. **`ApiError` 위에 새 뿌리 `ApiRequestError`를 둔다**
   - 장점: `ApiError`·`ClientError`·`ServerError`의 뜻과 필드가 그대로다. 새 실패 종류는 형제로 붙는다.
   - 단점: 뿌리 이름이 하나 는다. 호출처는 `ApiError`가 아니라 `ApiRequestError`를 잡아야 모든 요청 실패를 받는다.
4. **라이브러리는 그대로 두고 쓰는 쪽 앱이 감싼다**
   - 장점: 라이브러리 변경이 없다.
   - 단점: `BaseApiService`의 하위 클래스 다섯 개(buppy 둘, fancall·aidol·trade-safety 하나씩)가 같은 감싸기를 반복한다. 타입 구분은 모든 사용처가 같아야 의미가 있다.

## Decision

후보 3을 고른다. 요청 실패는 모두 `ApiRequestError`의 하위 타입으로 던진다. `ApiError`(HTTP 오류 응답, `ClientError`·`ServerError`), `NetworkError`(응답 없음), `InvalidResponseError`(응답은 왔으나 계약 위반)가 그 아래에 있다.

## Rationale

- 기존 `ApiError` 계열의 뜻과 필드를 바꾸지 않는 유일한 후보다. 후보 1·2는 지금 `ApiError`를 쓰는 코드의 의미나 타입을 바꾼다.
- 뿌리 하나로 "예상된 요청 실패"를 표현하면, 호출처의 규칙이 "`ApiRequestError`면 실패로 처리, 아니면 버그로 다시 던짐" 한 줄이 된다.
- 감싸기와 응답 본문 변환은 모든 사용처가 같아야 하는 동작이라 라이브러리가 정위치다(후보 4를 고르지 않은 이유).

## Consequences

- `BaseApiService.request`
  - `fetch` 거부와 응답 본문 읽기 실패는 `NetworkError`로 던진다. 원래 오류는 `cause`에 남는다.
  - 호출처가 `AbortSignal`로 취소한 요청(`AbortError`)은 실패가 아니므로 감싸지 않고 그대로 던진다.
  - `content-type`이 JSON인데 본문을 파싱하지 못하면 `InvalidResponseError`로 던진다.
  - `getAuthHeaders`의 오류는 요청 실패가 아니므로 감싸지 않는다.
- `BaseApiService.handleError`는 추상 메서드가 아니라 기본 구현을 갖는다. 응답 본문 `{detail, code}`를 읽어 5xx는 `ServerError`, 그 밖은 `ClientError`로 던진다. 본문이 JSON이 아니면 메시지는 상태 줄, 코드는 `INTERNAL_SERVER_ERROR`다. 하위 클래스는 401 처리처럼 필요한 것만 덮어쓴다.
- `BaseCrudRepository.validateResponse`는 스키마 검증 실패를 `InvalidResponseError`로 던진다. 메시지와 `errorReporter` 보고는 그대로다.
- 대상 빌드가 ES2020이라 `cause`는 `ErrorOptions`가 아니라 클래스 필드로 둔다.
- 보고 정책(어떤 실패를 오류 추적 도구에 보낼지)은 이 결정에 넣지 않는다. 지금처럼 하위 클래스가 정한다. 브라우저의 `NetworkError`는 오프라인 사용자에게 흔해서 서버와 기준이 다르기 때문이다.
- Python 패키지는 HTTP 클라이언트가 없어 해당하지 않는다.

하위 호환을 깨는 점과 마이그레이션:

- `request`가 던지는 타입이 `TypeError`·`SyntaxError`에서 `NetworkError`·`InvalidResponseError`로 바뀐다. 두 타입 모두 `Error`의 하위 타입이다. buppy·fancall·aidol·trade-safety의 프런트엔드에서 이 두 타입에 기대는 코드는 없었다(2026-11-15 검색).
- `validateResponse`가 던지는 타입이 `Error`에서 `InvalidResponseError`로 바뀐다. 메시지는 같다.
- 쓰는 쪽은 넓은 `catch`를 "`ApiRequestError`면 처리, 아니면 다시 던짐"으로 좁힌다. 자체 구현한 응답 본문 변환(예: buppy `readApiError`)은 기본 `handleError`로 대체할 수 있다.

## 재검토 조건

- 보고 정책을 라이브러리로 올릴 때. 이때 `NetworkError`를 기본으로 보고할지 환경별로 다시 정한다.
- 대상 빌드를 ES2022 이상으로 올릴 때. `cause`를 표준 `ErrorOptions`로 옮긴다.
- Python 패키지에 HTTP 클라이언트가 생길 때. 같은 계층을 맞출지 정한다.
