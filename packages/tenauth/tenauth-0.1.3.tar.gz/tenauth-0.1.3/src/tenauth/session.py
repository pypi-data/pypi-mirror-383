from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import AsyncContextManager
from uuid import UUID

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import AccessContext

SessionFactory = Callable[[], AsyncContextManager[AsyncSession]]


async def verify_access_context(
    session: AsyncSession, *, tenant_id: UUID, user_id: UUID
) -> None:
    """Ensure the session has the expected tenant/user GUCs applied."""
    res_user = await session.execute(
        text("SELECT current_setting('app.user_id', true)")
    )
    db_user = res_user.scalar()
    res_tenant = await session.execute(
        text("SELECT current_setting('app.tenant_id', true)")
    )
    db_tenant = res_tenant.scalar()
    if not db_user or not db_tenant:
        raise RuntimeError(
            f"Failed to bind access context: user_id={db_user!r}, tenant_id={db_tenant!r}"
        )
    if UUID(db_tenant) != tenant_id:
        raise RuntimeError(f"Tenant mismatch: {db_tenant} != {tenant_id}")
    if UUID(db_user) != user_id:
        raise RuntimeError(f"User mismatch: {db_user} != {user_id}")


async def apply_access_context(
    session: AsyncSession,
    *,
    access_context: AccessContext,
    verify: bool = True,
) -> None:
    """Apply tenant/user GUCs to the given session and persist metadata."""
    await session.execute(
        text("SELECT set_config('app.tenant_id', :tid, false)"),
        {"tid": str(access_context.tenant_id)},
    )
    await session.execute(
        text("SELECT set_config('app.user_id', :uid, false)"),
        {"uid": str(access_context.user_id)},
    )

    if verify:
        await verify_access_context(
            session,
            tenant_id=access_context.tenant_id,
            user_id=access_context.user_id,
        )

    session.info["tenant_id"] = access_context.tenant_id
    session.info["user_id"] = access_context.user_id


async def reset_access_context(session: AsyncSession) -> None:
    """Reset tenant/user GUCs and clear metadata on session close."""
    try:
        await session.execute(text("RESET app.user_id"))
        await session.execute(text("RESET app.tenant_id"))
    except Exception:
        # best-effort; connection close will drop the settings if this fails
        pass
    finally:
        session.info.pop("tenant_id", None)
        session.info.pop("user_id", None)


@asynccontextmanager
async def access_scoped_session_ctx(
    *,
    session_factory: SessionFactory,
    access_context: AccessContext,
    verify: bool = True,
) -> AsyncIterator[AsyncSession]:
    """Yield a session with tenant/user GUCs applied for the context lifetime."""
    async with session_factory() as session:
        await apply_access_context(
            session, access_context=access_context, verify=verify
        )
        try:
            yield session
        finally:
            await reset_access_context(session)
