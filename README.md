# AIoIA Core

FastAPI + Next.js 풀스택 프로젝트용 공통 인프라

## 설치

```bash
# Python
pip install -e git+https://github.com/algorima/aioia-core.git#subdirectory=python

# TypeScript
npm install file:./aioia-core/typescript
```

## Python

**5줄로 완전한 CRUD API (JWT, Sentry, OpenAPI 포함)**

```python
from aioia_core.fastapi import BaseCrudRouter

router = BaseCrudRouter(
    model_class=User, create_schema=UserCreate, update_schema=UserUpdate,
    db_session_factory=SessionLocal, manager_factory=UserManagerFactory(),
    role_provider=MyRoleProvider(), jwt_secret_key=settings.jwt_secret,
    resource_name="users", tags=["Users"]
)
app.include_router(router.get_router())

# GET /users, POST /users, GET /users/{id}, PATCH /users/{id}, DELETE /users/{id}
```

**복잡한 필터**

```python
# (role=admin AND active=true) OR email contains "@company.com"
filters = [{
    "operator": "or",
    "value": [
        {"operator": "and", "value": [
            {"field": "role", "operator": "eq", "value": "admin"},
            {"field": "active", "operator": "eq", "value": true}
        ]},
        {"field": "email", "operator": "contains", "value": "@company.com"}
    ]
}]
users, total = manager.get_all(filters=filters)
```

## TypeScript

**Zod 검증 + Sentry 통합**

```typescript
import { BaseCrudRepository } from "@aioia/core";
import { z } from "zod";

const userSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});

class UserRepository extends BaseCrudRepository<User> {
  resource = "users";
  protected getDataSchema() { return userSchema; }
}

const { data, total } = await repo.getList({
  filters: [{ field: "email", operator: "contains", value: "@company.com" }],
  sorters: [{ field: "createdAt", order: "desc" }]
});
```

## 주요 기능

### Python
- BaseCrudRouter: JWT 인증, 역할 기반 권한, Sentry, camelCase↔snake_case 자동 변환
- BaseManager: 페이지네이션, 정렬, 중첩 필터 (or/and), Protocol 기반 타입 안전성
- Pydantic ↔ SQLAlchemy 분리

### TypeScript
- BaseCrudRepository: Zod 런타임 검증, Sentry 에러 리포팅
- BaseApiService: Server/Client 환경 추상화, 토큰 갱신

## 요구사항

- Python 3.10-3.12, FastAPI 0.115+
- TypeScript 5+, Next.js 14+
- Sentry (필수)
- PostgreSQL 권장 (SQLite는 개발용)

## 제약사항

- TypeScript는 Next.js 환경 가정 (`NEXT_PUBLIC_*`)
- Sentry 비활성화 불가
- ID는 UUID string (int 자동 증가 아님)

## 라이선스

Apache 2.0
