"""
Пользовательские хендлеры: старт, оплата инвойсом, проверка заказов.
"""
from aiogram import Router, F
from aiogram.types import (
    Message,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)
import os

from backend import get_filepath_project
from models import async_session, PaymentRecord
from settings import settings
from payments import (
    get_price_rub,
    set_file_id,
    get_file_id_for_payment,
    list_successful_payments,
)


# Инициализация роутера
router_user = Router()
SUPPORT_LINK = settings.SUPPORT_LINK


async def build_payment_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для оплаты
    
    Returns:
        InlineKeyboardMarkup: Готовая клавиатура
    """
    keyboard_buttons = [
        [InlineKeyboardButton(text=f"Оплатить {get_price_rub()} ₽", callback_data="pay_invoice")],
        [InlineKeyboardButton(text="Проверить все заказы", callback_data="check_all_payments")],
        [InlineKeyboardButton(text="Техподдержка", url=SUPPORT_LINK)],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


@router_user.message(F.text == "/start")
async def handle_start(message: Message) -> None:
    """
    Обработчик команды /start
    
    Args:
        message: Объект сообщения
    """
    keyboard = await build_payment_keyboard()
    
    await message.answer(
        "📚 Курсовой проект по модулю 8: 'Анализ данных'\n"
        "Дисциплина: Разработка прикладного программного обеспечения\n\n"
        "🔹 Требования к оформлению:\n"
        "- Укажите ваше полное ФИО на титульном листе\n\n"
        "💳 После завершения оплаты бот отправит проект в чат\n\n"
        "❓ Возникли проблемы?\n"
        "Если оплата прошла, но проект не доступен - пожалуйста, обратитесь в техническую поддержку",
        reply_markup=keyboard,
    )


async def send_project_file(
    message: Message,
    payment_id: str,
    receipt_text: str,
) -> bool:
    """
    Отправляет файл проекта пользователю
    
    Args:
        message: Объект сообщения, в чат которого отправится файл
        payment_id: ID платежа
        receipt_text: Текст чека
        
    Returns:
        bool: Успешность отправки
    """
    cached_file_id = await get_file_id_for_payment(payment_id)
    if cached_file_id:
        await message.answer_document(cached_file_id, caption=receipt_text)
        return True
    
    try:
        file_path = await get_filepath_project()
        docx = FSInputFile(file_path, filename='Проект.docx')
        sent_message = await message.answer_document(docx, caption=receipt_text)
        
        # Очистка временного файла
        try:
            os.remove(file_path)
        except OSError:
            pass
        
        # Сохранение file_id для будущего использования
        file_id = sent_message.document.file_id
        await set_file_id(payment_id, file_id)
        return True
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке файла: {str(e)}")
        return False


@router_user.callback_query(F.data == "pay_invoice")
async def handle_pay_invoice(cb: CallbackQuery) -> None:
    await cb.answer()
    prices = [LabeledPrice(label="Проект", amount=int(get_price_rub()) * 100)]
    await cb.message.bot.send_invoice(
        chat_id=cb.message.chat.id,
        title="Оплата проекта",
        description="Покупка проекта по анализу данных",
        payload=f"user:{cb.from_user.id}",
        provider_token=settings.PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="buy_project",
    )


@router_user.callback_query(F.data == "check_all_payments")
async def handle_all_payments(cb: CallbackQuery) -> None:
    """
    Обработчик проверки всех платежей
    
    Args:
        cb: CallbackQuery объект
    """
    await cb.answer()
    
    # Берем только успешные платежи пользователя
    payments = await list_successful_payments(cb.from_user.id)

    if not payments:
        await cb.message.answer("У вас нет завершенных платежей.")
        return

    delivered_count = 0

    for payment in payments:
        payment_id = payment["payment_id"]
        receipt_text = f"Оплата через Telegram\nID: {payment_id}"
        if await send_project_file(cb.message, payment_id, receipt_text):
            delivered_count += 1

    if delivered_count > 0:
        await cb.message.answer(f"✅ Успешно отправлено {delivered_count} проектов!")
    else:
        await cb.message.answer("Не найдено успешных платежей для доставки.")


@router_user.pre_checkout_query()
async def handle_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@router_user.message(F.successful_payment)
async def handle_successful_payment(message: Message) -> None:
    sp = message.successful_payment
    payment_id = sp.telegram_payment_charge_id

    # Сохраняем успешный платеж
    async with async_session() as session:
        session.add(
            PaymentRecord(
                user_id=message.from_user.id,
                payment_id=payment_id,
            )
        )
        await session.commit()

    amount_rub = sp.total_amount / 100
    receipt_text = (
        f"Сумма: {amount_rub:.2f} ₽\n"
        f"ID: {payment_id}\n"
    )
    await send_project_file(message, payment_id, receipt_text)