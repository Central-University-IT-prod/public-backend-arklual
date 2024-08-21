"""This file starts the project"""

import asyncio
import logging
import sys
import time
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine
from handlers import not_understand
from handlers import users, start, main_menu, cancel, find_partners
from handlers.travels.main_menu import router
from models import base

TOKEN = 'TOKEN'
attemps = 0
ok = False
while not ok and attemps < 3:
    try:
        dp = Dispatcher(storage=RedisStorage.from_url('redis://default:secret@redis:6379/db'))
        ok = True
        print('Redis: ok')
    except Exception as e:
        attemps += 1
        print('Redis: ' + str(e))
        time.sleep(5)
if not ok:
    dp = Dispatcher(storage=MemoryStorage())


async def main():
    '''
    start method
    '''
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    ok_database = False
    while not ok_database:
        try:
            base.engine = create_engine("postgresql://db/postgres?user=postgres&password=secret", echo=True)
            ok_database = True
        except:
            await asyncio.sleep(5)
    dp.include_router(cancel.router)
    dp.include_routers(start.router, users.router, main_menu.router, find_partners.router, router)
    dp.include_router(not_understand.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
