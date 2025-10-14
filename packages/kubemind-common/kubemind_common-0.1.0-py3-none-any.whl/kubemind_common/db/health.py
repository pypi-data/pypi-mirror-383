from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def ping_db(session: AsyncSession) -> bool:
    try:
        res = await session.execute(text("SELECT 1"))
        res.scalar()
        return True
    except Exception:
        return False

