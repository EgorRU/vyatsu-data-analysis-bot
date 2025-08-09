"""
Модели SQLAlchemy: платежи и инициализация БД.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer


# Конфигурация базы данных
DATABASE_URL = "sqlite+aiosqlite:///database.db"

# Инициализация асинхронного движка SQLAlchemy
engine = create_async_engine(DATABASE_URL)

# Создание фабрики асинхронных сессий
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PaymentRecord(Base):
    """
    Модель для хранения информации о платежах.
    
    Атрибуты:
        id: Уникальный идентификатор записи
        user_id: ID пользователя (индексируется)
        payment_id: Уникальный идентификатор платежа
        file_id: ID привязанного файла (опционально)
    """
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        doc="ID пользователя"
    )
    payment_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        doc="Уникальный идентификатор платежа"
    )
    file_id: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
        doc="ID привязанного файла"
    )


async def init_db() -> None:
    """
    Инициализирует базу данных, создавая все таблицы.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)