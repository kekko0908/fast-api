const el = React.createElement;
const { useEffect, useState } = React;

const QUICK_TICKERS = ["IWDA", "SWDA", "VUAA", "IEMB", "EIMI"];

const formatPrice = (value, currency) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/d";
  }
  const formatted = Number(value).toLocaleString("it-IT", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });
  return currency ? `${formatted} ${currency}` : formatted;
};

const ResultCard = ({ data }) => {
  const title = data.resolved_ticker || data.ticker || "Ticker";
  const statusClass = data.found ? "pill" : "pill warn";
  const statusLabel = data.found ? "Disponibile" : "Non trovato";
  const metaItems = [
    el("span", { key: "status", className: statusClass }, statusLabel),
  ];

  if (data.category) {
    metaItems.push(el("span", { key: "category" }, data.category));
  }

  if (data.name) {
    metaItems.push(el("span", { key: "name" }, data.name));
  }

  return el(
    "div",
    { className: "card" },
    el("h3", null, title),
    el("div", { className: "meta" }, metaItems),
    el("div", { className: "price" }, formatPrice(data.price, data.currency)),
    el(
      "div",
      { className: "keyline" },
      data.error ? data.error : `Fonte: ${data.source || "scraper"}`
    )
  );
};

const App = () => {
  const [input, setInput] = useState("");
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("");
  const [statusTone, setStatusTone] = useState("info");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.body.classList.toggle("loading", loading);
  }, [loading]);

  const setInfo = (message) => {
    setStatus(message);
    setStatusTone("info");
  };

  const setError = (message) => {
    setStatus(message);
    setStatusTone("error");
  };

  const clearAll = () => {
    setInput("");
    setResults([]);
    setStatus("");
    setStatusTone("info");
  };

  const addChip = (value) => {
    const trimmed = input.trim();
    setInput(trimmed ? `${trimmed} ${value}` : value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const raw = input.trim();
    if (!raw) {
      setError("Inserisci almeno un ticker.");
      return;
    }

    const tickers = raw
      .split(/[,\s]+/)
      .map((value) => value.trim())
      .filter(Boolean);

    if (!tickers.length) {
      setError("Formato non valido.");
      return;
    }

    setLoading(true);
    setResults([]);
    setInfo(`Richiesta per ${tickers.length} ticker in corso...`);

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
      const data = Array.isArray(payload) ? payload : [payload];
      setResults(data);
      setInfo(`Completato: ${data.length} risultati.`);
    } catch (error) {
      setError(`Errore richiesta: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const statusPrefix = statusTone === "error" ? "Errore:" : "Info:";
  const statusNode = status
    ? [el("strong", { key: "label" }, statusPrefix), ` ${status}`]
    : "";

  const resultNodes =
    results.length > 0
      ? results.map((item, index) =>
          el(ResultCard, {
            key: `${item.ticker || "item"}-${index}`,
            data: item,
          })
        )
      : [
          el(
            "div",
            { className: "empty", key: "empty" },
            'Nessun risultato ancora. Inserisci un ticker e premi "Cerca prezzi".'
          ),
        ];

  return el(
    "div",
    { className: "shell" },
    el(
      "header",
      null,
      el(
        "div",
        null,
        el("h1", null, "FastAPI Markets Lab"),
        el(
          "p",
          { className: "subtitle" },
          "Inserisci uno o piu tickers, lancia la richiesta e vedi il risultato in tempo reale."
        )
      ),
      el("div", { className: "pill" }, "API /api/etf")
    ),
    el(
      "section",
      { className: "grid" },
      el(
        "div",
        { className: "panel" },
        el("h2", null, "Test rapido"),
        el(
          "form",
          { onSubmit: handleSubmit },
          el(
            "label",
            { htmlFor: "tickers" },
            "Tickers (separa con spazio o virgola)"
          ),
          el("input", {
            id: "tickers",
            name: "tickers",
            type: "text",
            placeholder: "Esempio: IWDA SWDA VUAA",
            autoComplete: "off",
            value: input,
            onChange: (event) => setInput(event.target.value),
          }),
          el(
            "div",
            { className: "actions" },
            el(
              "button",
              { className: "primary", type: "submit", disabled: loading },
              loading ? "Caricamento..." : "Cerca prezzi"
            ),
            el(
              "button",
              {
                className: "secondary",
                type: "button",
                onClick: clearAll,
              },
              "Pulisci"
            )
          )
        ),
        el(
          "div",
          { className: "hint" },
          "Suggerimenti rapidi:",
          el(
            "div",
            { className: "chips" },
            QUICK_TICKERS.map((ticker) =>
              el(
                "button",
                {
                  className: "chip",
                  type: "button",
                  key: ticker,
                  onClick: () => addChip(ticker),
                },
                ticker
              )
            )
          )
        ),
        el(
          "div",
          { className: "status", "aria-live": "polite" },
          statusNode
        )
      ),
      el(
        "div",
        { className: "panel" },
        el("h2", null, "Risultato"),
        el("div", { className: "results" }, resultNodes)
      )
    )
  );
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(el(App));
