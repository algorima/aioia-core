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

`BaseApiService.request`는 응답이 오지 않은 실패(`fetch` 거부, 본문 읽기 실패)와 응답 본문 파싱 실패를 감싸지 않고 원래 타입(`TypeError`, `SyntaxError`) 그대로 올린다. `BaseCrudRepository.validateResponse`는 응답 스키마 검증 실패를 일반 `Error`로 던진다. HTTP 오류 응답은 하위 클래스마다 `handleError`에서 따로 바꾸는데, 여섯 곳 중 다섯은 일반 `Error`(또는 `Error`를 상속한 자체 클래스나 응답 본문 객체)를 던지고 `ClientError`·`ServerError`를 던지는 곳은 buppy `ServerApiService` 하나다.

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
   - 단점: `BaseApiService`의 하위 클래스 여섯 개(buppy 둘, fancall·aidol·trade-safety·activity-timeblock 하나씩)가 같은 감싸기를 반복한다. 타입 구분은 모든 사용처가 같아야 의미가 있다.

## Decision

후보 3을 고른다. 요청 실패를 표현하는 타입은 모두 `ApiRequestError`의 하위 타입이다. `ApiError`(HTTP 오류 응답, `ClientError`·`ServerError`), `NetworkError`(응답 없음), `InvalidResponseError`(응답은 왔으나 계약 위반)가 그 아래에 있다. 라이브러리가 던지는 실패는 이 타입들이고, `handleError`를 덮어쓰는 하위 클래스도 오류 응답에 이 타입을 던진다.

## Rationale

- 기존 `ApiError` 계열의 뜻과 필드를 바꾸지 않는 유일한 후보다. 후보 1·2는 지금 `ApiError`를 쓰는 코드의 의미나 타입을 바꾼다.
- 뿌리 하나로 "예상된 요청 실패"를 표현하면, 호출처의 규칙이 "`ApiRequestError`면 실패로 처리, 아니면 버그로 다시 던짐" 한 줄이 된다.
- 감싸기와 응답 본문 변환은 모든 사용처가 같아야 하는 동작이라 라이브러리가 정위치다(후보 4를 고르지 않은 이유).

## Consequences

- `BaseApiService.request`
  - `fetch` 거부와 응답 본문 읽기 실패는 `NetworkError`로 던진다. 원래 오류는 `cause`에 남는다.
  - 호출처가 `AbortSignal`로 취소한 요청은 실패가 아니므로 감싸지 않고 취소 사유를 그대로 던진다. 신호가 취소됐으면 사유의 타입과 무관하게 취소로 본다(`abort(reason)`의 사용자 지정 사유 포함).
  - 단, 신호의 사유가 `TimeoutError`(`AbortSignal.timeout()`)면 응답이 제때 오지 않은 것이므로 `NetworkError`로 감싼다.
  - `content-type`이 JSON인데 본문을 파싱하지 못하면 `InvalidResponseError`로 던진다.
  - `getAuthHeaders`의 오류는 요청 실패가 아니므로 감싸지 않는다.
- `BaseApiService.handleError`는 추상 메서드가 아니라 기본 구현을 갖는다. 응답 본문을 읽어 5xx는 `ServerError`, 그 밖은 `ClientError`로 던진다. 변환은 `readApiError`로 분리해, 덮어쓰는 하위 클래스도 쓸 수 있다.
  - 읽는 본문은 셋이고 zod로 검증한다. `detail`이 문자열인 평평한 본문, `detail` 안에 `detail`·`code`가 든 본문(FastAPI가 dict `detail`의 `HTTPException`을 기본 처리기로 내는 모양, 이 레포 Python `BaseCrudRouter`가 처리기 없이 내는 모양), `detail`이 검증 오류 목록인 FastAPI 기본 422(메시지는 `msg`를 이어 붙이고, 코드가 없으면 `VALIDATION_ERROR`). `detail`과 `code`는 필드마다 따로 검증하므로, `code`가 문자열이 아니어도(예: `null`) 읽을 수 있는 `detail`은 버리지 않는다.
  - 그 밖의 본문(게이트웨이 HTML, 필드 타입이 다른 JSON)은 메시지를 상태 줄로, 코드를 `INTERNAL_SERVER_ERROR`로 둔다.
- `handleError`를 덮어쓰는 하위 클래스는 오류 응답에 `ApiRequestError` 하위 타입을 던져야 한다. `request`는 `handleError`가 던진 것을 감싸지 않는다. 감싸면 하위 클래스가 제어 흐름에 쓰는 오류가 바뀐다. 예를 들어 buppy `ClientApiService`는 `handleError`에서 던진 `SessionRefreshedError`를 `request`에서 잡아 재시도한다. 이 규칙을 지키지 않은 하위 클래스에서는 "`ApiRequestError`가 아니면 버그"라는 호출처 규칙이 성립하지 않는다.
- `BaseCrudRepository.validateResponse`는 스키마 검증 실패를 `InvalidResponseError`로 던진다. 메시지와 `errorReporter` 보고는 그대로다.
- 대상 빌드가 ES2020이라 `cause`는 `ErrorOptions`가 아니라 클래스 필드로 둔다.
- 보고 정책(어떤 실패를 오류 추적 도구에 보낼지)은 이 결정에 넣지 않는다. 지금처럼 하위 클래스가 정한다. 브라우저의 `NetworkError`는 오프라인 사용자에게 흔해서 서버와 기준이 다르기 때문이다.
- Python 패키지는 HTTP 클라이언트가 없어 해당하지 않는다.

하위 호환을 깨는 점과 마이그레이션:

- `request`가 던지는 타입이 `TypeError`·`SyntaxError`에서 `NetworkError`·`InvalidResponseError`로 바뀐다. 두 타입 모두 `Error`의 하위 타입이다.
- `validateResponse`가 던지는 타입이 `Error`에서 `InvalidResponseError`로 바뀐다. 메시지는 같다.
- 알려진 사용처(2026-11-15, 각 레포 기본 브랜치)와 해야 할 일:
  - buppy `frontend/src/aidol/lib/debut.ts`의 `isExpectedApiFailure`가 `instanceof TypeError`와 브라우저별 메시지로 네트워크 실패를 가른다. 3.0.0에서는 네트워크 단절이 `NetworkError`라 이 판별이 거짓이 되어 버그로 다시 던져진다. 버전을 올리는 PR에서 `instanceof ApiRequestError`로 바꾼다.
  - `handleError`를 덮어쓰고 일반 `Error`나 응답 본문 객체를 던지는 하위 클래스: buppy `ClientApiService`, fancall·aidol·trade-safety의 `ApiService`, activity-timeblock `SimpleApiService`(자체 `ApiError`가 `Error`를 상속). 버전을 올리는 PR에서 오류 응답을 `ClientError`·`ServerError`(또는 그 하위 타입)로 던지게 바꾼다. 기본 `handleError`나 `readApiError`를 쓰면 된다.
  - buppy `ServerApiService`는 이미 `ClientError`·`ServerError`를 던진다. 자체 `readApiError`는 기본 구현으로 대체할 수 있다.
  - buppy `debut.ts`의 `isAlreadyVotedError`는 `ClientApiService`가 409에서 응답 본문 객체를 그대로 던지는 것에 기대어 그 본문을 파싱한다. 409가 `ClientError`가 되면 이 판별이 거짓이 되어 "이미 투표함" 안내 대신 버그로 다시 던져진다. 같은 PR에서 `ClientError`의 `statusCode`·`errorCode`로 가르게 바꾼다.
  - buppy `ClientApiService`는 모든 403을 앱의 `QuotaExceededError`(`Error` 상속)로 바꾸고, 채팅방 페이지 두 곳이 이 타입으로 할당량 초과를 가른다. 백엔드는 할당량이 아닌 이유(권한 없음 등)로도 403을 내므로 지금도 오분류가 있고, 할당량 초과 응답(Flask `chatroom/blueprints.py`)은 `{"error": ...}` 본문이라 코드가 없다. 할당량은 HTTP 응답의 다른 타입이 아니라 오류의 종류이므로 `errorCode`로 가른다. 순서: 백엔드가 `{detail, code}`에 할당량 코드를 싣고 → 403 분기를 지워 기본 `ClientError`를 타게 하고 → 채팅방 두 곳을 `ClientError`와 `hasCode`로 바꾼 뒤 `QuotaExceededError`를 지운다.
- 순서: 하위 클래스가 위 규칙을 따른 뒤에 호출처의 넓은 `catch`를 "`ApiRequestError`면 처리, 아니면 다시 던짐"으로 좁힌다. 순서를 거꾸로 하면 HTTP 오류 응답이 버그로 다시 던져진다.

## 재검토 조건

- 보고 정책을 라이브러리로 올릴 때. 이때 `NetworkError`를 기본으로 보고할지 환경별로 다시 정한다.
- 대상 빌드를 ES2022 이상으로 올릴 때. `cause`를 표준 `ErrorOptions`로 옮긴다.
- Python 패키지에 HTTP 클라이언트가 생길 때. 같은 계층을 맞출지 정한다.
- 덮어쓴 `handleError`가 규칙을 지키지 않는 사례가 반복될 때. `request`가 비 `ApiRequestError`를 감싸고 제어 흐름 오류만 통과시키는 방식(예: 표식 인터페이스)을 다시 본다.
