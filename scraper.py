import asyncio
from playwright.async_api import async_playwright, Page, Browser
import time

URL_YIELD = "https://www.tradingview.com/symbols/TVC-US10Y/"
URL_GOLD = "https://www.tradingview.com/symbols/XAUUSD/"

SELECTOR_GOLD = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'
SELECTOR_YIELD = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'

browser = None
page = None
playwright_instance = None

latest_yield = None
latest_gold = None


async def init_browser():
    global browser, page, playwright_instance

    if browser is not None:
        return

    playwright_instance = await async_playwright().start()

    browser = await playwright_instance.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-breakpad",
            "--disable-client-side-phishing-detection",
            "--disable-default-apps",
            "--disable-hang-monitor",
            "--disable-popup-blocking",
            "--disable-prompt-on-repost",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=IsolateOrigins,site-per-process",
        ]
    )

    page = await browser.new_page()


async def background_refresh():
    global latest_yield, latest_gold, page

    next = o

    while True:
        try:
            # GOLD every 2 seconds
            if next%2 = 0
                await page.goto(URL_GOLD, wait_until="domcontentloaded")
                await page.wait_for_selector(SELECTOR_GOLD)
                latest_gold = await page.inner_text(SELECTOR_GOLD)

            # YIELD every 5 seconds
            if next%5 = 0
                await page.goto(URL_YIELD, wait_until="domcontentloaded")
                await page.wait_for_selector(SELECTOR_YIELD)
                latest_yield = await page.inner_text(SELECTOR_YIELD)

             next=next+1
        except Exception as e:
            print("Background refresh error:", e)

        await asyncio.sleep(1)


async def restart_browser():
    global browser, page, playwright_instance

    try:
        if page:
            await page.close()
        if browser:
            await browser.close()
        if playwright_instance:
            await playwright_instance.stop()
    except:
        pass

    browser = None
    page = None
    playwright_instance = None

    await init_browser()


background_task = None


async def periodic_restart():
    global background_task

    restart_time = 3600 * 2

    while True:
        await asyncio.sleep(restart_time)

        if background_task is not None:
            background_task.cancel()
            try:
                await background_task
            except:
                pass

        await restart_browser()

        background_task = asyncio.create_task(background_refresh())
