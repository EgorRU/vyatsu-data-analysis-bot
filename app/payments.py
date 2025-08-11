"""
Утилиты для платежей: цена, кэш file_id, выборка заказов.
"""
from typing import Optional, List
from settings import settings
from models import async_session, Payment


def get_price_rub() -> int:
    """
    Возвращает цену в рублях
    """
    return int(settings.PRICE_RUB)


async def set_file_id_for_provider(provider_payment_id: str, file_id: str) -> None:
    """
    Привязывает file_id к платежу
    """
    async with async_session() as session:
        await session.execute(
            Payment.__table__.update()
            .where(Payment.provider_payment_id == provider_payment_id)
            .values(file_id=file_id)
        )
        await session.commit()


async def get_file_id_for_provider(provider_payment_id: str) -> Optional[str]:
    """
    Возвращает file_id для платежа
    """
    async with async_session() as session:
        result = await session.execute(
            Payment.__table__.select()
            .where(Payment.provider_payment_id == provider_payment_id)
            .limit(1)
        )
        row = result.mappings().first()
        return row["file_id"] if row else None


async def list_successful_payments(user_id: int) -> List[dict]:
    """
    Получает список успешных платежей пользователя
    """
    async with async_session() as session:
        result = await session.execute(
            Payment.__table__.select()
            .where(Payment.user_id == user_id)
            .order_by(Payment.id.desc())
        )
        rows = list(result.mappings())
        return rows