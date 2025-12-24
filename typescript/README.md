# AIoIA Core (TypeScript)

AIoIA 프로젝트 공통 TypeScript 인프라 라이브러리

## 설치

```bash
npm install @aioia/core
```

## 포함 기능

- **Client**: BaseApiService (HTTP 통신, 에러 처리)
- **Repositories**: BaseCrudRepository (CRUD 패턴)
- **Components** (클라이언트 전용): LottiePlayer (Lottie 애니메이션 렌더링)

## 사용법

### 서버-세이프 모듈 (API, Repository)

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

### 클라이언트 컴포넌트 (use client 필수)

```typescript
"use client";

import { LottiePlayer } from "@aioia/core/client";

export default function AnimationComponent() {
  return (
    <LottiePlayer
      src="https://example.com/animation.json"
      loop
      autoplay
    />
  );
}
```

## 요구사항

- Node.js 18+
- TypeScript 5+
- React 18+ (peerDependency)
- Zod 3+ (peerDependency)

## 라이선스

Apache 2.0
