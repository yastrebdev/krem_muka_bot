from aiogram import html, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto, FSInputFile

from avito import send_avito_reply
from avito_chat_store import get_chat_url

from db.users import create_user, find_user_by_username

import os

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    username = message.from_user.username
    name = message.from_user.first_name

    await message.answer(f"Привет, {html.bold(message.from_user.first_name)}! 👋\n\n"
                         "Это бот для приёма заказов в кондитерской @kremmyka\n\n"
                         "Сделать заказ -- /new_order\n"
                         "Меню -- /menu\n"
                         "Примеры десертов -- /examples")

    user = await find_user_by_username(username)

    if not user:
        await create_user(username, name)


@router.message(Command('new_order'))
async def order(message: Message):
    await message.answer(text='Выберите что хотите заказать 🎂')


@router.message(Command('menu'))
async def menu(message: Message):
    folder_path = 'files/menu'
    media_group = []
    print(folder_path)
    # Получаем список файлов изображений из папки
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            file_path = os.path.join(folder_path, filename)
            photo = FSInputFile(file_path)
            media_group.append(InputMediaPhoto(media=photo))

    if media_group:
        await message.answer("Наш ассортимент 🎂")
        # Отправляем изображения плиткой
        await message.answer_media_group(media_group)
    else:
        await message.answer("Изображения не найдены 😔")


@router.message(Command('examples'))
async def menu(message: Message):
    await message.answer(text='Примеры готовых десертов 🎂')


@router.message(Command("answer"))
async def cmd_reply(message: types.Message):
    try:
        parts = message.text.split(maxsplit=2)
        _, chat_id, reply_text = parts
    except ValueError:
        await message.reply("⚠️ Формат: /ответ <chat_id> <текст>")
        return

    chat_url = get_chat_url(chat_id)
    if not chat_url:
        await message.reply("❌ Чат не найден.")
        return

    await message.reply("⏳ Переход в чат и отправка сообщения...")
    try:
        await send_avito_reply(chat_url, reply_text)
        await message.reply("✅ Ответ отправлен!")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")