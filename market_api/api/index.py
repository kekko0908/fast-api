from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scripts.scrape_prices import analizza_etf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TickerRequest(BaseModel):
    tickers: list[str]


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def fetch_ticker_data(ticker: str) -> dict[str, Any]:
    try:
        result = analizza_etf(ticker)
    except Exception as exc:
        return {
            "ticker": ticker,
            "found": False,
            "error": str(exc),
            "source": "yfinance",
        }

    if not result or not result.get("trovato"):
        return {
            "ticker": ticker,
            "found": False,
            "error": "Ticker non trovato.",
            "source": "yfinance",
        }

    price_value = result.get("prezzo")
    try:
        price = float(price_value) if price_value is not None else None
    except (TypeError, ValueError):
        price = None

    return {
        "ticker": ticker,
        "resolved_ticker": result.get("ticker"),
        "price": price,
        "currency": result.get("valuta"),
        "name": result.get("nome"),
        "category": result.get("categoria"),
        "found": True,
        "source": "yfinance",
    }


@app.get("/", include_in_schema=False)
def get_home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/etf/{ticker}")
def get_etf_data(ticker: str):
    return fetch_ticker_data(ticker)


@app.post("/api/etf")
def get_etf_batch(payload: TickerRequest):
    return [fetch_ticker_data(ticker) for ticker in payload.tickers]
