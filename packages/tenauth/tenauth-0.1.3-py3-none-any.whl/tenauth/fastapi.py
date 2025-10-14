from __future__ import annotations

from collections.abc import AsyncIterator, Callable

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import AccessContext, AuthContext
from .session import SessionFactory, access_scoped_session_ctx

bearer_scheme = HTTPBearer(auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> AuthContext:
    """Require Authorization header and return an AuthContext, else raise 401."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme = (credentials.scheme or "").lower()
    token = credentials.credentials
    if scheme != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    return AuthContext.from_token(token)


async def require_access_context(
    auth: AuthContext = Depends(require_auth),
) -> AccessContext:
    """Resolve tenant/user context from an AuthContext."""
    return AccessContext(tenant_id=auth.tid, user_id=auth.sub)


def build_access_scoped_session_dependency(
    session_factory: SessionFactory,
    *,
    verify: bool = True,
) -> Callable[..., AsyncIterator[AsyncSession]]:
    """Create a FastAPI dependency that yields a scoped session."""

    async def dependency(
        tenant: AccessContext = Depends(require_access_context),
    ) -> AsyncIterator[AsyncSession]:
        async with access_scoped_session_ctx(
            session_factory=session_factory,
            access_context=tenant,
            verify=verify,
        ) as session:
            yield session

    return dependency
