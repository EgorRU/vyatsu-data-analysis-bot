from aiogram import Router, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os
from settings import settings

from backend import get_filepath_project
from models import async_session, PaymentRecord
from payments import (
    generate_payment_link,
    get_price_rub,
    check_payment_status,
    get_payment,
    build_receipt_text,
    set_file_id,
    get_file_id_for_payment,
)


# Инициализация роутера
router_user = Router()
SUPPORT_LINK = settings.SUPPORT_LINK


class PurchaseState(StatesGroup):
    """Состояния процесса покупки"""
    waiting_for_payment = State()


async def build_payment_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для оплаты
    
    Args:
        user_id: ID пользователя
        
    Returns:
        InlineKeyboardMarkup: Готовая клавиатура
    """
    payment_url, payment_id = await generate_payment_link(
        user_id=user_id, 
        description="Оплата"
    )
    
    keyboard_buttons = [
        [InlineKeyboardButton(text=f"Оплата {get_price_rub()} ₽", url=payment_url)],
        [InlineKeyboardButton(text="Проверить все заказы", callback_data="check_all_payments")],
        [InlineKeyboardButton(text="Техподдержка", url=SUPPORT_LINK)],
    ]
    
    if payment_id:
        keyboard_buttons.insert(1, [
            InlineKeyboardButton(
                text="Проверить текущий заказ", 
                callback_data=f"check_current:{payment_id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


@router_user.message(F.text == "/start")
async def handle_start(message: Message):
    """
    Обработчик команды /start
    
    Args:
        message: Объект сообщения
    """
    keyboard = await build_payment_keyboard(message.from_user.id)
    
    await message.answer(
        "📚 Курсовой проект по модулю 8: 'Анализ данных'\n"
        "Дисциплина: Разработка прикладного программного обеспечения\n\n"
        "🔹 Требования к оформлению:\n"
        "- Укажите ваше полное ФИО на титульном листе\n\n"
        "💳 После завершения оплаты:\n"
        "1. Нажмите кнопку 'Проверить текущий заказ' для получения:\n"
        "   - Доступа к проекту\n"
        "   - Электронного чека\n\n"
        "❓ Возникли проблемы?\n"
        "Если оплата прошла, но проект не доступен - пожалуйста, обратитесь в техническую поддержку",
        reply_markup=keyboard,
    )


async def send_project_file(
    chat_id: int, 
    payment_id: str, 
    receipt_text: str
) -> bool:
    """
    Отправляет файл проекта пользователю
    
    Args:
        chat_id: ID чата
        payment_id: ID платежа
        receipt_text: Текст чека
        
    Returns:
        bool: Успешность отправки
    """
    cached_file_id = await get_file_id_for_payment(payment_id)
    if cached_file_id:
        await chat_id.answer_document(cached_file_id, caption=receipt_text)
        return True
    
    try:
        file_path = await get_filepath_project()
        docx = FSInputFile(file_path, filename='Проект.docx')
        sent_message = await chat_id.answer_document(docx, caption=receipt_text)
        
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
        await chat_id.answer(f"❌ Ошибка при отправке файла: {str(e)}")
        return False


@router_user.callback_query(F.data.startswith("check_current:"))
async def handle_current_payment(cb: CallbackQuery, state: FSMContext):
    """
    Обработчик проверки текущего платежа
    
    Args:
        cb: CallbackQuery объект
        state: Состояние FSM
    """
    await cb.answer()
    
    # Проверка состояния
    if await state.get_state() == PurchaseState.waiting_for_payment:
        await cb.message.answer("Пожалуйста, дождитесь завершения текущей проверки...")
        return

    await state.set_state(PurchaseState.waiting_for_payment)
    
    try:
        payment_id = cb.data.split(":")[1]
        status = await check_payment_status(payment_id)
        
        if status == "succeeded":
            payment = get_payment(payment_id)
            receipt_text = build_receipt_text(payment)
            await send_project_file(cb.message, payment_id, receipt_text)
        else:
            await cb.message.answer(f"Заказ {payment_id} не оплачен.")
            
    finally:
        await state.clear()


@router_user.callback_query(F.data == "check_all_payments")
async def handle_all_payments(cb: CallbackQuery, state: FSMContext):
    """
    Обработчик проверки всех платежей
    
    Args:
        cb: CallbackQuery объект
        state: Состояние FSM
    """
    await cb.answer()
    
    # Проверка состояния
    if await state.get_state() == PurchaseState.waiting_for_payment:
        await cb.message.answer("Пожалуйста, дождитесь завершения текущей проверки...")
        return

    await state.set_state(PurchaseState.waiting_for_payment)
    
    try:
        # Получаем все платежи пользователя
        async with async_session() as session:
            result = await session.execute(
                PaymentRecord.__table__.select()
                .where(PaymentRecord.user_id == cb.from_user.id)
                .order_by(PaymentRecord.id.desc())
            )
            payments = list(result.mappings())
        
        if not payments:
            await cb.message.answer("У вас нет завершенных платежей.")
            return
        
        delivered_count = 0
        
        # Обрабатываем каждый платеж
        for payment in payments:
            payment_id = payment["payment_id"]
            status = await check_payment_status(payment_id)
            
            if status == "succeeded":
                payment_obj = get_payment(payment_id)
                receipt_text = build_receipt_text(payment_obj)
                
                if await send_project_file(cb.message, payment_id, receipt_text):
                    delivered_count += 1
        
        # Итоговое сообщение
        if delivered_count > 0:
            await cb.message.answer(f"✅ Успешно отправлено {delivered_count} проектов!")
        else:
            await cb.message.answer("Не найдено успешных платежей для доставки.")
            
    finally:
        await state.clear()