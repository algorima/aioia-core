# AIoIA Core (Python)

AIoIA 프로젝트 공통 Python 인프라 라이브러리

## 설치

```bash
pip install aioia-core
```

## 포함 기능

- **Database**: SQLAlchemy Base, BaseModel, BaseManager (CRUD)
- **Errors**: 표준화된 에러 코드 및 응답
- **LLM**: OpenAI/Anthropic provider 추상화
- **Testing**: 테스트 인프라 (fixtures, managers)

## 사용법

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

## 요구사항

- Python 3.10-3.12

## 라이선스

Apache 2.0
