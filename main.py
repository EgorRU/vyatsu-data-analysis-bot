from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

from settings import settings
from models import init_db
from user import router_user


async def main() -> None:
    """Основная функция для запуска бота."""
    # Создание бд
    await init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN)
    dispatcher = Dispatcher(storage=MemoryStorage())
    
    # Подключение роутеров
    dispatcher.include_router(router_user)
    
    # Запуск бота
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())