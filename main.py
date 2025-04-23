import asyncio
import logging

from avito_monitor_messages import login_and_monitor
from handlers import routers
from bot import dp, bot
from handlers.set_commands import set_commands


async def main():
    for router in routers:
        dp.include_router(router)
    await asyncio.gather(
        login_and_monitor(),
        set_commands(bot),
        dp.start_polling(bot),
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')