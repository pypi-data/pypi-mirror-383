# srx-lib-core

Core utilities for SRX Python services. Small, generic helpers you can reuse across FastAPI-based microservices.

What it includes:
- Logging setup with loguru (`get_logger`, `setup_logger`)
- Base settings class with Pydantic Settings
- FastAPI app factory with sensible defaults (CORS, exception handling, health route)

## Install

PyPI (public):

- `pip install srx-lib-core`

Using uv (pyproject):

```
[project]
dependencies = ["srx-lib-core>=0.1.0"]
```

## Usage

Logging:

```
from srx_lib_core import get_logger
logger = get_logger(__name__)
logger.info("hello")
```

Settings:

```
from srx_lib_core import BaseServiceSettings

class Settings(BaseServiceSettings):
    OPENAI_API_KEY: str | None = None

settings = Settings()  # loads from .env by default
```

FastAPI app factory:

```
from fastapi import APIRouter
from srx_lib_core import create_app

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

app = create_app(title="my-service", routers=[router])
```

## Environment Variables

- `LOG_LEVEL` (default: `INFO`)
- `LOG_FILE` (optional path)
- `ENVIRONMENT` (default: `development`)
- `CORS_ORIGIN` (comma-separated origins; default empty)

## Release

This repo ships a GitHub Actions workflow that publishes to GitHub Packages on tags `v*`.

- Create a tag: `git tag v0.1.0 && git push --tags`
- The workflow uses `GITHUB_TOKEN` with `packages:write`.

## License

Proprietary © SRX
