from fastapi import FastAPI
import asyncio
from scraper import fetch_yield

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Playwright microservice running"}

@app.get("/yield")
async def get_yield():
    value = await fetch_yield()
    return {"yield": value}
