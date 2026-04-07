import asyncio
from playwright.async_api import async_playwright, Page, Browser

URL = "https://www.tradingview.com/symbols/TVC-US10Y/"
SELECTOR = 'span[data-qa-id="symbol-last-value"]'

browser: Browser | None = None
page: Page | None = None
playwright_instance = None


async def init_browser():
    """
    Launch a persistent browser at startup.
    """
    global browser, page, playwright_instance

    if browser is not None:
        return  # already initialized

    playwright_instance = await async_playwright().start()

    browser = await playwright_instance.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-gpu"]
    )

    page = await browser.new_page()
    await page.goto(URL, timeout=60000)
    await page.wait_for_selector(SELECTOR, timeout=60000)
    print("Browser initialized and TradingView loaded.")


async def fetch_yield():
    global browser, page

    if browser is None or page is None:
        await init_browser()

    try:
        # Just read the DOM — no reload
        el = await page.query_selector(SELECTOR)
        if el:
            return await el.inner_text()

        # If selector missing, try soft refresh
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector(SELECTOR, timeout=60000)
        el = await page.query_selector(SELECTOR)
        return await el.inner_text()

    except Exception as e:
        print("Error during fetch:", e)
        print("Restarting browser...")
        await restart_browser()
        return await fetch_yield()


async def restart_browser():
    """
    Fully restart browser if TradingView crashes.
    """
    global browser, page, playwright_instance

    try:
        if page:
            await page.close()
        if browser:
            await browser.close()
    except:
        pass

    browser = None
    page = None

    await init_browser()
