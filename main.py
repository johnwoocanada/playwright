from fastapi import FastAPI
from scraper import fetch_yield, fetch_gold

# Author: John
# local run on windows: 
# 1. python .\test_playwright.py
# 2. using docker container
# A. docker build -t playwright-test .
# B. docker run -p 8000:8000 playwright-test

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Playwright persistent browser running"}

@app.get("/yield")
async def get_yield():
    value = await fetch_yield()
    return {"yield": value}

@app.get("/gld")
async def get_gold():
    value = await fetch_gold()
    return {"gold": value}
