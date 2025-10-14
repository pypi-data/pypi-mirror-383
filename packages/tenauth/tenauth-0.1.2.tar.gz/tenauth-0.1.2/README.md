# Tenauth

![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-checked-5D2F86?logo=ruff&logoColor=white)
![isort](https://img.shields.io/badge/imports-isort-ef8336?logo=python&logoColor=white)
![Commitizen](https://img.shields.io/badge/commitizen-friendly-0f72ff?logo=git&logoColor=white)
![Gitleaks](https://img.shields.io/badge/secrets-gitleaks-f2552c?logo=git&logoColor=white)

Tenant-aware auth and database helpers for FastAPI services. Tenauth keeps JWT parsing, access context verification, and Postgres GUC management in one place so your routes can stay focused on business logic.

## Highlights
- Bearer token parsing into typed `AuthContext` models without wiring boilerplate.
- FastAPI dependencies for locking requests to tenant and user scopes.
- Async session helpers that apply and verify Postgres GUCs on every connection.
- DSN utilities to inject tenant metadata for workers, migrations, or tooling.
- Tight pytest coverage with ready-to-use JWT fixtures.

## Installation

```bash
uv pip sync
```

If `uv` is not available:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## FastAPI Quickstart

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from tenauth.fastapi import build_access_scoped_session_dependency, require_auth
from tenauth.schemas import AuthContext

engine = create_async_engine("postgresql+psycopg://svc@db/app", echo=False)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

app = FastAPI()

@asynccontextmanager
async def session_factory() -> AsyncIterator[AsyncSession]:
    session = sessionmaker()
    try:
        yield session
    finally:
        await session.close()

SessionDep = build_access_scoped_session_dependency(session_factory=session_factory)

@app.get("/me")
def read_profile(auth: AuthContext = Depends(require_auth)):
    return {"user_id": str(auth.sub), "tenant_id": str(auth.tid)}

@app.get("/widgets")
async def list_widgets(session: AsyncSession = Depends(SessionDep)):
    result = await session.execute("SELECT * FROM widgets LIMIT 20")
    return result.all()
```

The `require_auth` dependency validates `Authorization: Bearer` headers and returns an `AuthContext`. `build_access_scoped_session_dependency` binds tenant and user IDs to the session, verifies the applied GUCs, and resets them when the request completes.

## Database Sessions & Background Tasks

```python
from tenauth.schemas import AccessContext
from tenauth.session import access_scoped_session_ctx

async with access_scoped_session_ctx(
    session_factory=session_factory,
    access_context=AccessContext(tenant_id=tenant_uuid, user_id=user_uuid),
) as session:
    await session.execute(...)
```

For DSN-based tooling, inject tenant metadata directly:

```python
from tenauth.tenancy import dsn_with_tenant

tenant_dsn = dsn_with_tenant(base_dsn, tenant_uuid)
```

## Testing

```bash
uv run pytest
```

Use `uv run pytest -k <keyword>` during focused iterations. Async cases should be marked with `pytest.mark.asyncio`.

## Development Workflow
- Install the Git hooks via `uv run pre-commit install` and run `uv run pre-commit run --all-files` before pushing.
- Ruff (`ruff-format`, `ruff-check`) and `isort` keep the codebase consistent; they run automatically through pre-commit.
- `gitleaks` guards against committing secrets, and Commitizen enforces conventional commit messages (`cz commit`).
- Review additional design notes and module guides under `docs/`.

To preview the documentation site locally:

```bash
uv run mkdocs serve
```
