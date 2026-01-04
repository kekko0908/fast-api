import os
import re
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

INDEX_HTML = """<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>FastAPI Markets Lab</title>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,500;6..72,700&family=Space+Grotesk:wght@400;600;700&display=swap");

      :root {
        color-scheme: light;
        --ink: #101416;
        --muted: #52616b;
        --panel: #f6f2ea;
        --panel-strong: #efe4d3;
        --brand: #0f6b5f;
        --brand-soft: #5bb59b;
        --accent: #d97c3f;
        --shadow: 0 18px 40px rgba(16, 20, 22, 0.12);
        --radius: 20px;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Newsreader", serif;
        color: var(--ink);
        background: radial-gradient(circle at 15% 20%, #f7ede2 0%, transparent 45%),
          radial-gradient(circle at 80% 10%, #f0f6f4 0%, transparent 40%),
          linear-gradient(140deg, #f5f1e8 0%, #eef2f0 35%, #f3e7da 100%);
      }

      .shell {
        max-width: 1080px;
        margin: 0 auto;
        padding: 48px 28px 64px;
        display: grid;
        gap: 28px;
      }

      header {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
      }

      h1 {
        margin: 0;
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(28px, 4vw, 44px);
        letter-spacing: -0.02em;
      }

      .subtitle {
        max-width: 520px;
        color: var(--muted);
        font-size: 1.05rem;
      }

      .grid {
        display: grid;
        gap: 24px;
      }

      @media (min-width: 900px) {
        .grid {
          grid-template-columns: 1fr 1.1fr;
          align-items: start;
        }
      }

      .panel {
        background: var(--panel);
        border-radius: var(--radius);
        padding: 28px;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
      }

      .panel::after {
        content: "";
        position: absolute;
        inset: 14px;
        border-radius: calc(var(--radius) - 6px);
        border: 1px solid rgba(16, 20, 22, 0.08);
        pointer-events: none;
      }

      .panel h2 {
        margin: 0 0 8px;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.2rem;
      }

      label {
        display: block;
        font-size: 0.95rem;
        color: var(--muted);
        margin-bottom: 10px;
      }

      input[type="text"] {
        width: 100%;
        padding: 14px 16px;
        font-size: 1rem;
        border-radius: 14px;
        border: 1px solid rgba(16, 20, 22, 0.15);
        background: #fff;
        font-family: "Space Grotesk", sans-serif;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
      }

      input[type="text"]:focus {
        outline: none;
        border-color: var(--brand);
        box-shadow: 0 0 0 4px rgba(15, 107, 95, 0.15);
      }

      .actions {
        margin-top: 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: center;
      }

      button {
        border: none;
        border-radius: 999px;
        padding: 12px 20px;
        font-size: 0.95rem;
        font-family: "Space Grotesk", sans-serif;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      button.primary {
        background: var(--brand);
        color: #fff;
        box-shadow: 0 10px 18px rgba(15, 107, 95, 0.28);
      }

      button.secondary {
        background: #fff;
        color: var(--ink);
        border: 1px solid rgba(16, 20, 22, 0.15);
      }

      button:active {
        transform: translateY(1px);
      }

      .hint {
        margin-top: 18px;
        padding: 14px 16px;
        border-radius: 16px;
        background: var(--panel-strong);
        color: var(--muted);
        font-size: 0.95rem;
      }

      .chips {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .chip {
        padding: 6px 12px;
        border-radius: 999px;
        background: #fff;
        border: 1px dashed rgba(16, 20, 22, 0.2);
        font-family: "Space Grotesk", sans-serif;
        font-size: 0.85rem;
        cursor: pointer;
      }

      .status {
        margin-top: 18px;
        font-size: 0.92rem;
        color: var(--muted);
        min-height: 24px;
      }

      .status strong {
        color: var(--ink);
      }

      .results {
        display: grid;
        gap: 16px;
      }

      .empty {
        padding: 22px;
        border-radius: 18px;
        border: 1px dashed rgba(16, 20, 22, 0.18);
        color: var(--muted);
        background: rgba(255, 255, 255, 0.6);
      }

      .card {
        padding: 20px;
        border-radius: 18px;
        background: #fff;
        box-shadow: 0 12px 24px rgba(16, 20, 22, 0.1);
        animation: rise 0.5s ease both;
      }

      .card h3 {
        margin: 0 0 6px;
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.05rem;
      }

      .meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        font-size: 0.92rem;
        color: var(--muted);
      }

      .pill {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-family: "Space Grotesk", sans-serif;
        background: rgba(15, 107, 95, 0.12);
        color: var(--brand);
      }

      .pill.warn {
        background: rgba(217, 124, 63, 0.18);
        color: var(--accent);
      }

      .price {
        font-size: 1.6rem;
        font-family: "Space Grotesk", sans-serif;
        margin: 12px 0 6px;
      }

      .keyline {
        margin-top: 14px;
        border-top: 1px solid rgba(16, 20, 22, 0.08);
        padding-top: 12px;
        font-size: 0.9rem;
        color: var(--muted);
      }

      .loading .primary {
        opacity: 0.7;
        cursor: progress;
      }

      @keyframes rise {
        from {
          opacity: 0;
          transform: translateY(12px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .reveal {
        opacity: 0;
        transform: translateY(12px);
        animation: reveal 0.6s ease forwards;
      }

      .reveal:nth-child(2) {
        animation-delay: 0.08s;
      }

      .reveal:nth-child(3) {
        animation-delay: 0.16s;
      }

      @keyframes reveal {
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <header class="reveal">
        <div>
          <h1>FastAPI Markets Lab</h1>
          <p class="subtitle">
            Inserisci uno o piu tickers, lancia la richiesta e vedi il risultato
            in tempo reale.
          </p>
        </div>
        <div class="pill">API /api/etf</div>
      </header>

      <section class="grid">
        <div class="panel reveal">
          <h2>Test rapido</h2>
          <form id="ticker-form">
            <label for="tickers">Tickers (separa con spazio o virgola)</label>
            <input
              id="tickers"
              name="tickers"
              type="text"
              placeholder="Esempio: IWDA SWDA VUAA"
              autocomplete="off"
            />
            <div class="actions">
              <button class="primary" type="submit">Cerca prezzi</button>
              <button class="secondary" type="button" id="clear">Pulisci</button>
            </div>
          </form>
          <div class="hint">
            Suggerimenti rapidi:
            <div class="chips">
              <button class="chip" type="button" data-value="IWDA">IWDA</button>
              <button class="chip" type="button" data-value="SWDA">SWDA</button>
              <button class="chip" type="button" data-value="VUAA">VUAA</button>
              <button class="chip" type="button" data-value="IEMB">IEMB</button>
              <button class="chip" type="button" data-value="EIMI">EIMI</button>
            </div>
          </div>
          <div class="status" id="status" aria-live="polite"></div>
        </div>

        <div class="panel reveal">
          <h2>Risultato</h2>
          <div class="results" id="results">
            <div class="empty" id="empty">
              Nessun risultato ancora. Inserisci un ticker e premi "Cerca prezzi".
            </div>
          </div>
        </div>
      </section>
    </div>

    <script>
      const form = document.querySelector("#ticker-form");
      const input = document.querySelector("#tickers");
      const results = document.querySelector("#results");
      const statusBox = document.querySelector("#status");
      const empty = document.querySelector("#empty");
      const clearBtn = document.querySelector("#clear");
      const chips = document.querySelectorAll(".chip");

      const setStatus = (message, tone = "info") => {
        if (!message) {
          statusBox.textContent = "";
          return;
        }
        const prefix = tone === "error" ? "Errore:" : "Info:";
        statusBox.innerHTML = `<strong>${prefix}</strong> ${message}`;
      };

      const setLoading = (isLoading) => {
        document.body.classList.toggle("loading", isLoading);
      };

      const formatPrice = (value, currency) => {
        if (value === null || value === undefined) {
          return "n/d";
        }
        const formatted = Number(value).toLocaleString("it-IT", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 4,
        });
        return currency ? `${formatted} ${currency}` : formatted;
      };

      const renderResult = (data) => {
        const card = document.createElement("div");
        card.className = "card";

        const header = document.createElement("div");
        const title = document.createElement("h3");
        title.textContent = data.resolved_ticker || data.ticker || "Ticker";
        header.appendChild(title);

        const meta = document.createElement("div");
        meta.className = "meta";

        const status = document.createElement("span");
        status.className = data.found ? "pill" : "pill warn";
        status.textContent = data.found ? "Disponibile" : "Non trovato";
        meta.appendChild(status);

        if (data.category) {
          const category = document.createElement("span");
          category.textContent = data.category;
          meta.appendChild(category);
        }

        if (data.name) {
          const name = document.createElement("span");
          name.textContent = data.name;
          meta.appendChild(name);
        }

        const price = document.createElement("div");
        price.className = "price";
        price.textContent = formatPrice(data.price, data.currency);

        const foot = document.createElement("div");
        foot.className = "keyline";
        foot.textContent = data.error
          ? data.error
          : `Fonte: ${data.source || "scraper"}`;

        card.appendChild(header);
        card.appendChild(meta);
        card.appendChild(price);
        card.appendChild(foot);

        results.appendChild(card);
      };

      const clearResults = () => {
        results.innerHTML = "";
        empty.style.display = "block";
      };

      chips.forEach((chip) => {
        chip.addEventListener("click", () => {
          const value = chip.dataset.value;
          if (!value) {
            return;
          }
          const current = input.value.trim();
          input.value = current ? `${current} ${value}` : value;
          input.focus();
        });
      });

      clearBtn.addEventListener("click", () => {
        input.value = "";
        setStatus("");
        clearResults();
      });

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const raw = input.value.trim();
        if (!raw) {
          setStatus("Inserisci almeno un ticker.", "error");
          return;
        }

        const tickers = raw
          .split(/[,\s]+/)
          .map((value) => value.trim())
          .filter(Boolean);

        if (!tickers.length) {
          setStatus("Formato non valido.", "error");
          return;
        }

        clearResults();
        empty.style.display = "none";
        setStatus(`Richiesta per ${tickers.length} ticker in corso...`);
        setLoading(true);

        try {
          const response = await fetch("/api/etf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tickers }),
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          const payload = await response.json();
          payload.forEach(renderResult);
          setStatus(`Completato: ${payload.length} risultati.`);
        } catch (error) {
          setStatus(`Errore richiesta: ${error.message}`, "error");
        } finally {
          setLoading(false);
        }
      });
    </script>
  </body>
</html>
"""


SCRAPER_PATH = "scripts" / "scrape_prices.py"
PYTHON_BIN = os.environ.get("PYTHON_BIN", "python")


def run_scraper_text(ticker: str) -> str:
    command = [PYTHON_BIN, "-X", "utf8", str(SCRAPER_PATH)]
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8:ignore"
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            command,
            input=f"{ticker}\nq\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
            check=False,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Python non disponibile sul server.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Timeout scraper.") from exc

    if result.returncode != 0:
        error = (result.stderr or "").strip()
        raise RuntimeError(error or "Scraper fallito.")

    output = (result.stdout or "").strip()
    if not output:
        raise RuntimeError("Output scraper vuoto.")
    return output


def parse_price(value: str) -> float | None:
    cleaned = value.replace(",", ".")
    cleaned = re.sub(r"[^0-9.]", "", cleaned)
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    return parsed if parsed == parsed else None


def parse_scraper_output(output: str, input_ticker: str) -> dict:
    found = bool(re.search(r"TROVATO\s*:", output, re.IGNORECASE))
    if re.search(r"ticker non trovato", output, re.IGNORECASE):
        return {
            "ticker": input_ticker,
            "found": False,
            "error": "Ticker non trovato.",
            "source": "scrape_prices.py",
        }

    resolved_match = re.search(r"TROVATO\s*:\s*([A-Z0-9.:\-_]+)", output)
    name_match = re.search(r"Nome\s*:\s*(.+)", output)
    type_match = re.search(r"Tipo\s*:\s*(.+)", output)
    price_match = re.search(r"Prezzo\s*:\s*([0-9.,]+)\s*([A-Z]{3})?", output)

    price = parse_price(price_match.group(1)) if price_match else None
    currency = price_match.group(2) if price_match and price_match.group(2) else None

    result = {
        "ticker": input_ticker,
        "resolved_ticker": resolved_match.group(1) if resolved_match else None,
        "price": price,
        "currency": currency,
        "name": name_match.group(1).strip() if name_match else None,
        "category": type_match.group(1).strip() if type_match else None,
        "found": found or price is not None,
        "source": "scrape_prices.py",
    }
    if not result["found"]:
        result["error"] = "Output scraper non riconosciuto."
    return result


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def get_home():
    return HTMLResponse(INDEX_HTML)


@app.get("/api/etf/{ticker}")
def get_etf_data(ticker: str):
    output = run_scraper_text(ticker)
    return parse_scraper_output(output, ticker)


@app.post("/api/etf")
def get_etf_batch(payload: TickerRequest):
    results: list[dict[str, Any]] = []
    for ticker in payload.tickers:
        try:
            output = run_scraper_text(ticker)
            results.append(parse_scraper_output(output, ticker))
        except Exception as exc:
            results.append(
                {
                    "ticker": ticker,
                    "found": False,
                    "error": str(exc),
                    "source": "scrape_prices.py",
                }
            )
    return results
