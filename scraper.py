import asyncio
import datetime
from playwright.async_api import async_playwright, Page, Browser


URL_YIELD = "https://www.tradingview.com/symbols/TVC-US10Y/"
URL_GOLD = "https://www.tradingview.com/symbols/XAUUSD/"

SELECTOR_GOLD = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'
SELECTOR_YIELD = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'

browser = None
page_gold = None
page_yield = None
playwright_instance = None

latest_yield = None
latest_gold = None

timeout_3_second = 3000

background_task = None
restart_task = None

async def init_browser():
    global browser, page_gold, page_yield, playwright_instance

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

    page_gold = await browser.new_page()
    page_yield = await browser.new_page()

    await page_gold.goto(URL_GOLD, wait_until="domcontentloaded", timeout=timeout_3_second)
    await page_yield.goto(URL_YIELD, wait_until="domcontentloaded", timeout=timeout_3_second)


async def background_refresh():
    global latest_yield, latest_gold, page_gold, page_yield

    next = 0
    print(f"Background refresh started @ {datetime.datetime.now()}")

    while True:
        try:
            # GOLD every 2 seconds
            if next % 2 == 0:
                await page_gold.reload(wait_until="domcontentloaded", timeout=timeout_3_second)
                await page_gold.wait_for_selector(SELECTOR_GOLD, timeout=timeout_3_second)
                latest_gold = await page_gold.inner_text(SELECTOR_GOLD)

            # YIELD every 5 seconds
            if next % 5 == 0:
                await page_yield.goto(URL_YIELD, wait_until="domcontentloaded", timeout=timeout_3_second)
                await page_yield.wait_for_selector(SELECTOR_YIELD, timeout=timeout_3_second)
                latest_yield = await page_yield.inner_text(SELECTOR_YIELD)

        except Exception as e:
            print(f"Background refresh error: {e}")
        finally:
            next += 1
            await asyncio.sleep(1)


async def restart_browser():
    global browser, page_gold, page_yield, playwright_instance

    try:
        if page_gold:
            await page_gold.close()
        if page_yield:
            await page_yield.close()
        if browser:
            await browser.close()
        if playwright_instance:
            await playwright_instance.stop()
    except Exception as e:
        print(f"Error closing browser @ {datetime.datetime.now()}: {e}")

    browser = None
    page_gold = None
    page_yield = None
    playwright_instance = None

    await init_browser()


async def periodic_restart():
    global background_task

    restart_time = 3600
    total_restart = 0

    while True:
        await asyncio.sleep(restart_time)
        total_restart = total_restart + 1
        print(f"Restart browser # {total_restart} @ {datetime.datetime.now()}")

        if background_task is not None:
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                print(f"Background task cancelled @ {datetime.datetime.now()}")
            except Exception as e:
                print(f"Error cancelling background taskc @ {datetime.datetime.now()}: {e}")

        await restart_browser()

        background_task = asyncio.create_task(background_refresh())
