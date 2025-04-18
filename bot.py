# aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# system
from config import BOT_TOKEN, CHAT_ID
import aiohttp
from avito_chat_store import add_chat
from uuid import uuid4

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


async def send_to_telegram(text: str, href: str):
    chat_id = str(uuid4())[:8]  # генерим короткий ID для ответа
    add_chat(chat_id, f"https://www.avito.ru{href}")

    message = f"<b>Новое сообщение на Avito</b>\n\nЧат ID: <code>{chat_id}</code>\n<a href='https://www.avito.ru{href}'>Открыть чат</a>\n\n{text}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)