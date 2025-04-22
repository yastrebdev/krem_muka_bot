import re


async def filter_ur_messages(page):
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