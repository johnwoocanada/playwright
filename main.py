from fastapi import FastAPI
import asyncio
from scraper import init_browser, fetch_yield

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Launch persistent browser once
    asyncio.create_task(init_browser())

@app.get("/")
def root():
    return {"status": "ok", "message": "Playwright persistent browser running"}

@app.get("/yield")
async def get_yield():
    value = await fetch_yield()
    return {"yield": value}
