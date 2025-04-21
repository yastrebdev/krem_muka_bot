import asyncio
import re

from playwright.async_api import async_playwright, TimeoutError

from utils.send_from_avito_to_telegram import send
from config import (
    AVITO_LOGIN,
    AVITO_PASSWORD,
    AVITO_MESSENGER_URL, AVITO_PROFILE_URL)

avito_page = None
avito_ready = asyncio.Event()

async def fill_input_safe(page, selector, value, label=""):
    try:
        print(f"🔍 Ждём поле: {label or selector}")
        await page.wait_for_selector(selector, timeout=15000, state='visible')
        await page.fill(selector, value)
        print(f"✅ Введено: {label or selector}")
        return True
    except TimeoutError:
        print(f"❌ Не найдено поле {label or selector}")
        return False


async def login_and_monitor():
    global avito_page

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        avito_page = page

        print("🌐 Переход на страницу входа...")
        try:
            await page.goto(
                AVITO_MESSENGER_URL,
                timeout=60000,
                wait_until="domcontentloaded"
            )
        except Exception as e:
            print(f"⚠️ Ошибка при переходе на {AVITO_MESSENGER_URL}: {e}")
            return

        if "profile" in page.url and "login" not in page.url:
            print("✅ Уже авторизованы")
            await page.goto(AVITO_MESSENGER_URL)
        else:
            await page.wait_for_load_state("domcontentloaded")
            print("🔐 Ожидаем форму входа...")

            login_filled = await fill_input_safe(
                page,
                'input[type="tel"], input[type="text"]',
                AVITO_LOGIN,
                "Логин")
            if login_filled:
                await page.click('button[type="submit"]')

                password_filled = await fill_input_safe(
                    page,
                    'input[type="password"]',
                    AVITO_PASSWORD,
                    "Пароль")
                if password_filled:
                    await page.click('button[type="submit"]')

                    print("⏳ Ожидаем вход/редирект...")
                    for _ in range(30):
                        if page.url.startswith(AVITO_PROFILE_URL):
                            break
                        await page.wait_for_timeout(1000)

                    if not page.url.startswith(AVITO_PROFILE_URL):
                        print("⚠️ Похоже, нужно вручную ввести капчу или код из СМС.")
                        while not page.url.startswith(AVITO_PROFILE_URL):
                            await asyncio.sleep(2)
                            print("🕵️ Ожидаем вход...")

            else:
                print("❌ Не удалось найти поля входа. Страница могла измениться.")

        print("📨 Переходим в мессенджер...")
        await page.goto(AVITO_MESSENGER_URL)
        try:
            await page.wait_for_selector(
                '[data-marker="channels/channelLink"]',
                timeout=20000)
        except TimeoutError:
            print("⚠️ Сообщения не загружены.")

        await page.wait_for_selector('.controls-grid-row_3cells-HiV_Z')
        filters = await page.query_selector_all('[data-marker="unreadFilter/toggleButton"]')

        for f in filters:
            filter_text = await f.inner_text()
            clean_text = re.sub(r'\s+', ' ', filter_text).strip()

            if "Все сообщения" in clean_text:
                await f.click()
                break

        await page.wait_for_selector('button[data-marker="unreadFilter/custom-option(unread)"]')

        unread_button = page.locator('button[data-marker="unreadFilter/custom-option(unread)"]')
        await unread_button.click()

        messages = await page.query_selector_all('[data-marker="channels/channelLink"]')
        print(f"📬 Найдено сообщений: {len(messages)}")
        for i, msg in enumerate(messages[:5]):
            content = await msg.inner_text()
            print(f"✉️ [{i+1}] {content[:100]}...")

        print("⏳ Начинаем мониторинг входящих сообщений...\n")
        last_messages = set()

        while True:
            await page.wait_for_timeout(10000)

            messages = await page.query_selector_all('[data-marker="channels/channelLink"]')
            current_texts = set()

            for msg in messages[:10]:
                text = (await msg.inner_text()).strip()
                href = await msg.get_attribute("href")  # ссылка на чат
                message_id = href or "[no_id]"

                current_texts.add(text)

                if text not in last_messages:
                    full_text = f"<b>Новое сообщение на Авито</b>\n\n{message_id}\n\n{text}"
                    print(f"🔔 Отправка в Telegram:\n{full_text}\n{'-'*40}")
                    await send(full_text, href)

            last_messages = current_texts


avito_ready.set()


async def send_avito_reply(chat_url, reply_text):
    await avito_ready.wait()
    print(2, avito_page)
    if avito_page is None:
        print("⚠️ avito_page еще не инициализирован")
        return

    await avito_page.goto(chat_url, wait_until="domcontentloaded")
    await avito_page.wait_for_selector('[data-marker="reply/input"]', timeout=10000)

    input_box = await avito_page.query_selector('[data-marker="reply/input"]')
    await input_box.fill(reply_text)
    await input_box.press("Enter")


if __name__ == "__main__":
    asyncio.run(login_and_monitor())
