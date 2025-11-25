# AIoIA Core

AIoIA 프로젝트 공통 인프라 라이브러리

## 포함 기능

### Python
- **Database**: SQLAlchemy Base, BaseModel, BaseManager (CRUD)
- **Errors**: 표준화된 에러 코드 및 응답
- **LLM**: OpenAI/Anthropic provider 추상화

### TypeScript
- **Client**: BaseApiService (HTTP 통신)
- **Repositories**: BaseCrudRepository (CRUD 패턴)
- **Types**: Repository 타입 정의

## 설치

### Python

```bash
# Git 서브모듈
git submodule add https://github.com/algorima/aioia-core.git
pip install -e ./aioia-core/python
```

### TypeScript

```json
{
  "dependencies": {
    "@aioia/core": "file:./aioia-core/typescript"
  }
}
```

## 사용법

### Python

```python
from aioia_core.database import BaseModel, BaseManager
from aioia_core.errors import ErrorResponse, RESOURCE_NOT_FOUND
from aioia_core.llm import ModelSettings, OpenAIProvider

# SQLAlchemy 모델
class MyModel(BaseModel):
    __tablename__ = "my_table"
    name: Mapped[str] = mapped_column(String)

# LLM 사용
provider = OpenAIProvider()
model = provider.init_chat_model(
    ModelSettings(chat_model="gpt-4o", temperature=0.7),
    api_key="sk-..."
)
```

### TypeScript

```tsx
import { BaseCrudRepository, BaseApiService } from "@aioia/core";

class MyRepository extends BaseCrudRepository<MyModel, MyCreateData, MyUpdateData> {
  constructor(apiService: BaseApiService) {
    super("my-resource", mySchema, apiService);
  }
}
```

## 요구사항

- Python 3.10-3.12
- TypeScript 5+
- React 18+ (TypeScript 패키지)

## 라이선스

Apache 2.0
