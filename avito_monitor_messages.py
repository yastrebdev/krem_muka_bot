import asyncio

from playwright.async_api import async_playwright, TimeoutError

from avito_functions import (
    fill_input_safe, filter_ur_messages, read_messages
)

from utils.send_from_avito_to_telegram import send
from config import (
    AVITO_LOGIN,
    AVITO_PASSWORD,
    AVITO_MESSENGER_URL, AVITO_PROFILE_URL
)

avito_page = None
avito_ready = asyncio.Event()


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

            login_filled = await fill_input_safe(page,
                'input[type="tel"],'
                'input[type="text"]',
                AVITO_LOGIN,
                "Логин")
            if login_filled:
                await page.click('button[type="submit"]')

                password_filled = await fill_input_safe(page,
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

        await filter_ur_messages(page)

        print("⏳ Начинаем мониторинг входящих сообщений...\n")

        while True:
            await page.wait_for_timeout(500)

            current_texts = set()

            await page.wait_for_selector('[data-marker="channels/channelLink"]', timeout=0)
            messages = await page.query_selector_all('[data-marker="channels/channelLink"]')

            if messages:
                for msg in messages:
                    text = (await msg.inner_text()).strip()
                    href = await msg.get_attribute("href")
                    message_id = href or "[no_id]"

                    current_texts.add(text)

                    full_text = f"<b>Новое сообщение на Авито</b>\n\n{message_id}\n\n{text}"
                    print(f"🔔 Отправка в Telegram:\n{full_text}\n{'-'*40}")
                    await send(full_text, href)

            try:
                await read_messages(page)
            except:
                pass


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
