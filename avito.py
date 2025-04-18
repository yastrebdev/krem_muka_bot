import asyncio
from playwright.async_api import async_playwright, TimeoutError

from bot import send_to_telegram

AVITO_LOGIN_URL = "https://www.avito.ru/profile/login"
AVITO_MESSENGER_URL = "https://www.avito.ru/profile/messenger"
LOGIN = "79538055851"
PASSWORD = "strbvMv_25"

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
    print(1, avito_page)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()
        avito_page = page

        print("🌐 Переход на страницу входа...")
        try:
            await page.goto(
                AVITO_MESSENGER_URL,
                timeout=60000,  # 60 секунд
                wait_until="domcontentloaded"  # не ждем всей графики и рекламы
            )
        except Exception as e:
            print(f"⚠️ Ошибка при переходе на {AVITO_MESSENGER_URL}: {e}")
            return  # или restart / notify / pass

        # Если уже вошли — сразу в мессенджер
        if "profile" in page.url and "login" not in page.url:
            print("✅ Уже авторизованы")
            await page.goto(AVITO_MESSENGER_URL)
        else:
            # Иногда поля появляются внутри iframe — проверим на всякий
            await page.wait_for_load_state("domcontentloaded")
            print("🔐 Ожидаем форму входа...")

            # Используем более устойчивые селекторы
            login_filled = await fill_input_safe(page, 'input[type="tel"], input[type="text"]', LOGIN, "Логин")
            if login_filled:
                await page.click('button[type="submit"]')

                password_filled = await fill_input_safe(page, 'input[type="password"]', PASSWORD, "Пароль")
                if password_filled:
                    await page.click('button[type="submit"]')

                    # Ждём редиректа в профиль
                    print("⏳ Ожидаем вход/редирект...")
                    for _ in range(30):  # до 30 сек
                        if page.url.startswith("https://www.avito.ru/profile"):
                            break
                        await page.wait_for_timeout(1000)

                    if not page.url.startswith("https://www.avito.ru/profile"):
                        print("⚠️ Похоже, нужно вручную ввести капчу или код из СМС.")
                        while not page.url.startswith("https://www.avito.ru/profile"):
                            await asyncio.sleep(2)
                            print("🕵️ Ожидаем вход...")

            else:
                print("❌ Не удалось найти поля входа. Страница могла измениться.")

        print("📨 Переходим в мессенджер...")
        await page.goto(AVITO_MESSENGER_URL)
        try:
            await page.wait_for_selector('[data-marker="channels/channelLink"]', timeout=20000)
        except TimeoutError:
            print("⚠️ Сообщения не загружены.")

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
                    await send_to_telegram(full_text, href)

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
