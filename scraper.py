import asyncio
from playwright.async_api import async_playwright, Page, Browser

# Author: John

URL_YIELD = "https://www.tradingview.com/symbols/TVC-US10Y/"
URL_GOLD = "https://www.tradingview.com/symbols/XAUUSD/"

SELECTOR_YIELD = 'span[data-qa-id="symbol-last-value"]'
SELECTOR_GOLD = 'span[data-qa-id="symbol-last-value"]'


browser = None
page_yield = None
page_gold = None
playwright_instance = None

async def init_browser():
    global browser, page_yield, page_gold, playwright_instance

    if browser is not None:
        return

    playwright_instance = await async_playwright().start()

    browser = await playwright_instance.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-gpu"]
    )

    # Tab 1 — US10Y
    page_yield = await browser.new_page()
    await page_yield.goto(URL_YIELD, timeout=60000)
    await page_yield.wait_for_selector(SELECTOR_YIELD, timeout=60000)

    # Tab 2 — Gold
    page_gold = await browser.new_page()
    await page_gold.goto(URL_GOLD, timeout=60000)
    await page_gold.wait_for_selector(SELECTOR_GOLD, timeout=60000)

    print("Browser initialized with US10Y + XAUUSD tabs.")


async def fetch_yield():
    global browser, page_yield

    if browser is None or page_yield is None:
        await init_browser()

    try:
        # Just read the DOM — no reload
        el = await page_yield.query_selector(SELECTOR_YIELD)
        if el:
            return await el.inner_text()

        # If selector missing, try soft refresh
        await page_yield.goto(URL, timeout=60000)
        await page_yield.wait_for_selector(SELECTOR_YIELD, timeout=60000)
        el = await page_yield.query_selector(SELECTOR_YIELD)
        return await el.inner_text()

    except Exception as e:
        print("Error during fetch:", e)
        print("Restarting browser...")
        await restart_browser()
        return await fetch_yield()

async def fetch_gold():
    global browser, page_gold

    if browser is None or page_gold is None:
        await init_browser()

    try:
        el = await page_gold.query_selector(SELECTOR_GOLD)
        if el:
            txt = await el.inner_text()
            return txt.replace(",", "")  # clean formatting

        # Soft recovery
        await page_gold.goto(URL_GOLD, timeout=60000)
        await page_gold.wait_for_selector(SELECTOR_GOLD, timeout=60000)
        el = await page_gold.query_selector(SELECTOR_GOLD)
        return (await el.inner_text()).replace(",", "")

    except Exception as e:
        print("Gold fetch error:", e)
        await restart_browser()
        return await fetch_gold()

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
