from typing import Optional, List
from yookassa import Configuration, Payment
from settings import settings
from models import async_session, PaymentRecord


# Инициализация конфигурации платежной системы
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def is_payments_configured() -> bool:
    """Проверяет, настроены ли платежные реквизиты"""
    return bool(settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


async def get_active_payment_id(user_id: int) -> Optional[str]:
    """
    Получает ID активного платежа пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        ID платежа или None, если активных платежей нет
    """
    async with async_session() as session:
        result = await session.execute(
            PaymentRecord.__table__.select()
            .where(
                (PaymentRecord.user_id == user_id) & 
                (PaymentRecord.status.in_(["pending", "waiting_for_capture"]))
            )
            .order_by(PaymentRecord.id.desc())
            .limit(1)
        )
        row = result.mappings().first()
        return row["payment_id"] if row else None


async def get_undelivered_successful_payments(user_id: int) -> List[dict]:
    """
    Получает список успешных платежей без привязанных файлов
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список словарей с данными платежей
    """
    async with async_session() as session:
        result = await session.execute(
            PaymentRecord.__table__.select()
            .where(
                (PaymentRecord.user_id == user_id) & 
                (PaymentRecord.status == "succeeded") & 
                (PaymentRecord.file_id.is_(None))
            )
            .order_by(PaymentRecord.id.asc())
        )
        return list(result.mappings())


def get_price_rub() -> int:
    """Возвращает цену в рублях"""
    return int(settings.PRICE_RUB)


async def set_file_id(payment_id: str, file_id: str) -> None:
    """
    Привязывает file_id к платежу
    
    Args:
        payment_id: ID платежа
        file_id: ID файла для привязки
    """
    async with async_session() as session:
        await session.execute(
            PaymentRecord.__table__.update()
            .where(PaymentRecord.payment_id == payment_id)
            .values(file_id=file_id)
        )
        await session.commit()


async def get_file_id_for_payment(payment_id: str) -> Optional[str]:
    """
    Получает file_id для платежа
    
    Args:
        payment_id: ID платежа
        
    Returns:
        ID привязанного файла или None
    """
    async with async_session() as session:
        result = await session.execute(
            PaymentRecord.__table__.select()
            .where(PaymentRecord.payment_id == payment_id)
            .limit(1)
        )
        row = result.mappings().first()
        return row["file_id"] if row else None


async def generate_payment_link(user_id: int, description: str) -> tuple[str, str]:
    """
    Генерирует ссылку на оплату
    
    Args:
        user_id: ID пользователя
        description: Описание платежа
        
    Returns:
        Кортеж (ссылка для оплаты, ID платежа)
    """
    if not is_payments_configured():
        return "https://yookassa.ru/", ""

    # Проверяем существующий активный платеж
    existing_payment_id = await get_active_payment_id(user_id)
    if existing_payment_id:
        try:
            existing_payment = Payment.find_one(existing_payment_id)
            existing_status = getattr(existing_payment, "status", "unknown")
            
            if existing_status in ("pending", "waiting_for_capture"):
                confirmation = getattr(existing_payment, "confirmation", None)
                confirmation_url = getattr(confirmation, "confirmation_url", None)
                if confirmation_url:
                    return confirmation_url, existing_payment_id
        except Exception:
            pass 

    # Создаем новый платеж
    payment = Payment.create({
        "amount": {"value": settings.PRICE_RUB, "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": settings.BOT_URL},
        "description": description,
    })

    # Сохраняем платеж в БД
    async with async_session() as session:
        session.add(PaymentRecord(
            user_id=user_id, 
            payment_id=payment.id, 
            status=str(payment.status))
        )
        await session.commit()
        
    return payment.confirmation.confirmation_url, payment.id


async def check_payment_status(payment_id: str) -> str:
    """
    Проверяет и обновляет статус платежа
    
    Args:
        payment_id: ID платежа
        
    Returns:
        Текущий статус платежа
    """
    if not is_payments_configured():
        return "unavailable"
    
    try:
        payment = Payment.find_one(payment_id)
        if not payment:
            return "unknown"
        
        status = getattr(payment, "status", "unknown")
        
        # Обновляем статус в БД
        async with async_session() as session:
            await session.execute(
                PaymentRecord.__table__.update()
                .where(PaymentRecord.payment_id == payment_id)
                .values(status=str(status))
            )
            await session.commit()
        
        return str(status)
    except Exception as e:
        print(f"Ошибка при проверке статуса платежа {payment_id}: {e}")
        return "unknown"


def get_payment(payment_id: str) -> Optional[Payment]:
    """
    Получает объект платежа из API ЮKassa
    
    Args:
        payment_id: ID платежа
        
    Returns:
        Объект Payment или None
    """
    if not is_payments_configured():
        return None
        
    try:
        return Payment.find_one(payment_id)
    except Exception:
        return None


def build_receipt_text(payment: Optional[Payment]) -> str:
    """
    Формирует текст чека для платежа
    
    Args:
        payment: Объект платежа
        
    Returns:
        Текст чека
    """
    if payment is None:
        return ""
        
    pid = getattr(payment, "id", "")
    created_at = getattr(payment, "created_at", "")
    
    return "\n".join([
        f"ID: {pid}",
        f"Дата: {created_at}",
    ])


async def list_successful_payments(user_id: int) -> List[dict]:
    """
    Получает список успешных платежей пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список платежей в виде словарей
    """
    async with async_session() as session:
        result = await session.execute(
            PaymentRecord.__table__.select()
            .where(
                (PaymentRecord.user_id == user_id) & 
                (PaymentRecord.status == "succeeded"))
            .order_by(PaymentRecord.id.desc())
        )
        return list(result.mappings())