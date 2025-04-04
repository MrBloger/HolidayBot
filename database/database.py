from typing import Union, Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config_data import get_db_url

class Base(DeclarativeBase):
    pass

def create_engine() -> AsyncEngine:
    return create_async_engine(url=get_db_url(), echo=True, pool_pre_ping=True)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[Union[AsyncSession, Any]]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=True)


async def init_models():
    engine = create_engine()
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)