from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import scraper

# Author: John
# local run on windows: 
# 1. python .\test_playwright.py
# 2. using docker container
# A. docker build -t playwright-test .
# B. docker run -p 8000:8000 playwright-test

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await scraper.init_browser()
    scraper.background_task = asyncio.create_task(scraper.background_refresh())
    scraper.restart_task = asyncio.create_task(scraper.periodic_restart())

    yield

    # Shutdown
    scraper.background_task.cancel()
    scraper.restart_task.cancel()
    try:
        await scraper.background_task
        await scraper.restart_task
    except:
        pass

    await scraper.restart_browser()  # closes browser + playwright

app = FastAPI(lifespan=lifespan)

@app.get("/yield")
async def get_yield():
    return {"yield": scraper.latest_yield}

@app.get("/gld")
async def get_gold():
    return {"gold": scraper.latest_gold}
