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