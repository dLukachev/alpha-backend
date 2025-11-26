import asyncio
import os

from sqlalchemy import (
    ForeignKey,
    String,
    BigInteger,
    Integer,
    Boolean,
    DateTime,
)
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(
    url=os.getenv("DATABASE_URL"),
    echo=False,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Results(Base):
    __tablename__ = "results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[str] = mapped_column(String, nullable=False)
    time_create: Mapped[DateTime] = mapped_column(DateTime, default=None)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(async_main())
