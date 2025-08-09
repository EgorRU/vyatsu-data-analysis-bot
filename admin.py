"""
Админские хендлеры: выдача проекта без оплаты и выдача по ID платежа.
"""

from aiogram import Router, F
from aiogram.types import Message
from functools import lru_cache
from typing import Set

from settings import settings
from payments import get_file_id_for_payment
from user import send_project_file
from models import async_session, PaymentRecord


router_admin = Router()


@lru_cache(maxsize=1)
def get_admin_ids() -> Set[int]:
    """
    Возвращает множество ID администраторов, распарсенное из настроек.
    Результат кэшируется на время жизни процесса.
    """
    try:
        return {int(x.strip()) for x in settings.ADMIN_IDS.split(",") if x.strip()}
    except ValueError:
        return set()


def is_admin(user_id: int) -> bool:
    """
    Проверяет наличие пользователя в списке администраторов.
    Возвращает True, если `user_id` присутствует в `ADMIN_IDS`.
    """
    return user_id in get_admin_ids()


@router_admin.message(F.text == "/admin_get_project")
async def admin_get_project(message: Message) -> None:
    """
    Отправляет администратору проект без проверки оплаты.
    Используется для ручной выдачи материалов.
    """
    if not is_admin(message.from_user.id):
        return
    await send_project_file(message, payment_id="admin-free", receipt_text="Админ-выдача без оплаты")


@router_admin.message(F.text.startswith("/admin_get_by_id"))
async def admin_get_by_id(message: Message) -> None:
    """
    Отправляет проект по идентификатору платежа.
    Формат: /admin_get_by_id <проект id>
    """
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /admin_get_by_id <проект id>")
        return

    payment_id = parts[1].strip()
    if not payment_id:
        await message.answer("ID не валиден.")
        return

    # Проверяем, что такой платеж существует в БД
    async with async_session() as session:
        result = await session.execute(
            PaymentRecord.__table__.select()
            .where(PaymentRecord.payment_id == payment_id)
            .limit(1)
        )
        row = result.mappings().first()

    if not row:
        await message.answer("ID не найден или не валиден.")
        return

    # Попытка использовать кэшированный file_id
    file_id = await get_file_id_for_payment(payment_id)
    receipt_text = f"Админ-выдача по платежу\nID: {payment_id}"

    if file_id:
        await message.answer_document(file_id, caption=receipt_text)
        return

    await send_project_file(message, payment_id=payment_id, receipt_text=receipt_text)