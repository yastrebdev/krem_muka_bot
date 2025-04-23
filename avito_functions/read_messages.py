async def read_messages(page):
    await page.wait_for_selector('[data-marker="channels/channelLink"]')
    label = page.get_by_label("Выбрать все чаты")
    await label.click()

    await page.wait_for_selector("button[data-marker='bulk-actions/markRead']", timeout=2000)
    mark_read_button = page.locator("button[data-marker='bulk-actions/markRead']")
    await mark_read_button.click()