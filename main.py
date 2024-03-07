import asyncio

import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from motor.motor_asyncio import AsyncIOMotorClient

from handlers.client import router as client_router
from handlers.admin import router as admin_router


async def main():

    load_dotenv()

    bot = Bot(os.getenv("TOKEN"))
    dp = Dispatcher()

    cluster = AsyncIOMotorClient(host=os.getenv("HOST"), port=int(os.getenv("PORT")))
    database = cluster.flazemoviesdb

    dp.include_routers(
        client_router,
        admin_router
    )

    print("Бот запущен")

    await bot.delete_webhook(True)   # skip_updates=True
    await dp.start_polling(bot, db=database)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Пока")

