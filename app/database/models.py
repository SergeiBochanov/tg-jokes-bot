from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger)
    is_banned: Mapped[bool] = mapped_column()
    task_type: Mapped[str] = mapped_column(String(12))
    task: Mapped[str] = mapped_column(String(50))
    answer: Mapped[str] = mapped_column(String(50))

async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)