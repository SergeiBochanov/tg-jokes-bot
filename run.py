import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from app.handlers import router
from app.admin_handlers import admin_router
from app.database.models import async_main
from app.postcards import scheduler_func
from keep_alive import keep_alive
keep_alive()

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(fsm_strategy=FSMStrategy.CHAT)

async def main():
    await async_main()
    dp.include_router(admin_router)
    dp.include_router(router)
    await scheduler_func()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
