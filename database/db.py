import os

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession)
from sqlalchemy.orm import DeclarativeBase

from dotenv import load_dotenv


load_dotenv()

DATABASE = os.getenv('DATABASE')

engine = create_async_engine(DATABASE, echo=True)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
