import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database import create_engine, get_session_maker
from database.database import init_models
from middleware import DbSessionMiddleware
from config_data.config import settings
from handlers import user_handlers, other_handlers
from keyboards.main_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='{filename}:{lineno} #{levelname:8} '
                '[{asctime}] - {name} - {message}',
        style='{'
    )
    
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    
    # Инициализируем бот и диспетчер
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Настраиваем главное меню бота
    await set_main_menu(bot)
    
    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)
    
    # Инициализируем базу данных
    await init_models()
    
    # Настраиваем подключение к базе данных
    async_engine = create_engine()
    session_maker = get_session_maker(async_engine)
    
    # Добавляем middleware для работы с базой данных
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')