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
from settings import settings


# Конфигурация базы данных из настроек
DATABASE_URL = settings.DATABASE_URL

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


class Payment(Base):
    """
    Модель для хранения информации о платежах.
    
    Атрибуты:
        id: Уникальный идентификатор записи
        user_id: ID пользователя (индексируется)
        username: Username пользователя в Telegram (опционально)
        provider_payment_id: Идентификатор платежа у банка/провайдера
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
    username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Username пользователя"
    )
    provider_payment_id: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        unique=True,
        doc="ID платежа у провайдера/банка"
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