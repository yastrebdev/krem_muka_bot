import asyncio
import logging

from handlers import routers
from bot import dp, bot


async def main():
    for router in routers:
        dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')