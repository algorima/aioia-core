# AIoIA Core (TypeScript)

AIoIA 프로젝트 공통 TypeScript 인프라 라이브러리

## 설치

```bash
npm install @aioia/core
```

## 포함 기능

- **Client**: BaseApiService (HTTP 통신, 에러 처리)
- **Repositories**: BaseCrudRepository (CRUD 패턴)

## 사용법

```typescript
import { BaseCrudRepository, BaseApiService } from "@aioia/core";

// API Service
const apiService = new BaseApiService("/api");

// Repository
class MyRepository extends BaseCrudRepository<MyModel, MyCreateData, MyUpdateData> {
  constructor(apiService: BaseApiService) {
    super("my-resource", mySchema, apiService);
  }
}
```

## 요구사항

- Node.js 18+
- TypeScript 5+
- React 18+ (peerDependency)
- Zod 3+ (peerDependency)

## 라이선스

Apache 2.0
