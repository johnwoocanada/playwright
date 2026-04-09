import asyncio
import scraper

async def main():
    await scraper.init_browser()

    # Start background loop
    task = asyncio.create_task(scraper.background_refresh())

    # Wait long enough for first refresh cycle
    await asyncio.sleep(3)

    print("Yield:", scraper.latest_yield)
    print("Gold:", scraper.latest_gold)

    task.cancel()

asyncio.run(main())
