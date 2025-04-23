from aiogram.types import BotCommand
from aiogram import Bot


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запуск бота"),
        BotCommand(command="/new_order", description="Сделать заказ"),
        BotCommand(command="/menu", description="Открыть меню"),
        BotCommand(command="/examples", description="Примеры десертов"),
        BotCommand(command="/help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)