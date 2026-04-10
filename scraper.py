import asyncio
import datetime
from playwright.async_api import async_playwright


URL_YIELD = "https://www.tradingview.com/symbols/TVC-US10Y/"
URL_GOLD  = "https://www.tradingview.com/symbols/XAUUSD/"

SELECTOR_GOLD  = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'
SELECTOR_YIELD = 'span.js-symbol-last[data-qa-id="symbol-last-value"]'

UA_GOLD  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
UA_YIELD = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

browser           = None
page_gold         = None
page_yield        = None
playwright_instance = None

latest_yield = None
latest_gold  = None

background_task = None
restart_task    = None

TIMEOUT = 15000  # 15s — only used during initial page load

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
            "--disable-sync",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=IsolateOrigins,site-per-process",
        ]
    )

    context_gold = await browser.new_context(
        user_agent=UA_GOLD,
        viewport={"width": 1280, "height": 800}
    )
    context_yield = await browser.new_context(
        user_agent=UA_YIELD,
        viewport={"width": 1280, "height": 800}
    )

    page_gold  = await context_gold.new_page()
    page_yield = await context_yield.new_page()

    # Load ONCE here, don't reload in background_refresh
    await page_gold.goto(URL_GOLD,   wait_until="domcontentloaded", timeout=TIMEOUT)
    await page_yield.goto(URL_YIELD, wait_until="domcontentloaded", timeout=TIMEOUT)

    # Wait for price element to appear before returning
    try:
        await page_gold.wait_for_selector(SELECTOR_GOLD,   state="visible", timeout=TIMEOUT)
        await page_yield.wait_for_selector(SELECTOR_YIELD, state="visible", timeout=TIMEOUT)
        print(f"Browser initialized @ {datetime.datetime.now()}")
    except Exception as e:
        print(f"Warning: selector not visible on init: {e}")

async def background_refresh():
    global latest_yield, latest_gold

    next_tick = 0
    print(f"Background refresh started @ {datetime.datetime.now()}")

    while True:
        try:
            # GOLD every 2 seconds — just read DOM, no reload
            if next_tick % 2 == 0:
                el = await page_gold.query_selector(SELECTOR_GOLD)
                if el:
                    val = await el.inner_text()
                    if val:
                        latest_gold = val

            # YIELD every 5 seconds — just read DOM, no reload
            if next_tick % 5 == 0:
                el = await page_yield.query_selector(SELECTOR_YIELD)
                if el:
                    val = await el.inner_text()
                    if val:
                        latest_yield = val

        except Exception as e:
            print(f"Background refresh error: {e}")
        finally:
            next_tick += 1
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
    finally:
        browser           = None
        page_gold         = None
        page_yield        = None
        playwright_instance = None

    await init_browser()


async def periodic_restart():
    global background_task

    restart_time  = 14400  # 4 hours — less frequent restart = less blind periods
    total_restart = 0

    while True:
        await asyncio.sleep(restart_time)
        total_restart += 1
        print(f"Restart browser #{total_restart} @ {datetime.datetime.now()}")

        if background_task is not None:
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                print(f"Background task cancelled @ {datetime.datetime.now()}")
            except Exception as e:
                print(f"Error cancelling background task @ {datetime.datetime.now()}: {e}")

        await restart_browser()
        background_task = asyncio.create_task(background_refresh())
