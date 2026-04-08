import asyncio
from scraper import init_browser, fetch_yield, fetch_gold

async def main():
    await init_browser()
    print("Yield:", await fetch_yield())
    print("Gold:", await fetch_gold())

asyncio.run(main())
