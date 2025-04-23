import json
from uuid import uuid4
from avito_functions.avito_chat_store import add_chat
from config import BOT_TOKEN, CHAT_ID
import aiohttp


async def send(text: str, href: str):
    chat_id = str(uuid4())[:8]
    add_chat(chat_id, f"https://www.avito.ru{href}")

    message = f"Чат ID: <code>{chat_id}</code>\n<a href='https://www.avito.ru{href}'>Открыть чат</a>\n\n{text}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✍️ Ответить", "callback_data": f"accept:{chat_id}"},
            ]
        ]
    }

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": json.dumps(reply_markup)
    }

    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)