# Contributing to AIoIA Core

## Development Setup

### Python

```bash
cd python
poetry install
poetry run pytest
poetry run mypy aioia_core
poetry run pylint aioia_core
```

### TypeScript

```bash
cd typescript
npm install
npm test
npm run type-check
```

## Code Standards

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode, explicit types
- **Testing**: Write tests for new features
- **Documentation**: Update docstrings and README

## Pull Requests

1. Create feature branch from `main`
2. Write tests
3. Ensure all checks pass
4. Submit PR with clear description

## License

Apache 2.0 - See LICENSE file
