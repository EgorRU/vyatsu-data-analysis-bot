"""
Админский хендлер: команда /proj с опциональным аргументом ID платежа.

Без аргумента — сгенерировать и отправить новый проект.
С аргументом — отправить файл по указанному ID платежа (или сгенерировать и привязать, если отсутствует file_id).
"""

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from functools import lru_cache
from typing import Set
import os

from settings import settings
from payments import get_file_id_for_provider
from user import send_project_file
from models import async_session, Payment
from backend import get_filepath_project


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


@router_admin.message(F.text.startswith("/proj"))
async def admin_proj(message: Message) -> None:
    """
    /proj [<payment_id>]

    - Без аргумента: сгенерировать новый проект и отправить его администратору
    - С аргументом: отправить файл по ID платежа (или сгенерировать и привязать)
    """
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=1)

    # Случай: без аргумента — просто сгенерировать и отправить
    if len(parts) == 1:
        try:
            file_path = await get_filepath_project()
            docx = FSInputFile(file_path)
            await message.answer_document(docx, caption="Админ-генерация проекта")
        finally:
            try:
                os.remove(file_path)
            except Exception:
                pass
        return

    # С аргументом — ожидаем provider_payment_id
    provider_payment_id = parts[1].strip()
    if not provider_payment_id:
        await message.answer("ID не валиден.")
        return

    # Проверяем, что запись о платеже существует
    async with async_session() as session:
        result = await session.execute(
            Payment.__table__.select()
            .where(Payment.provider_payment_id == provider_payment_id)
            .limit(1)
        )
        row = result.mappings().first()

    if not row:
        await message.answer("ID не найден или не валиден.")
        return

    # Если file_id уже сохранен — отправляем его
    file_id = await get_file_id_for_provider(provider_payment_id)
    receipt_text = f"Админ-выдача по платежу\nID: {provider_payment_id}"
    if file_id:
        await message.answer_document(file_id, caption=receipt_text)
        return

    # Иначе генерируем проект, отправляем и привязываем file_id к платежу
    await send_project_file(message, provider_payment_id=provider_payment_id, receipt_text=receipt_text)