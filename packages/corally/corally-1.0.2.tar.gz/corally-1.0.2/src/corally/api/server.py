import os
import time
import csv
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=str(data_dir / "api.log"),      # Log file name
    filemode="w",            # Overwrite log file on each start
    format="%(asctime)s %(levelname)s %(message)s"
)

# .env laden
load_dotenv()
API_KEY = os.getenv("API_KEY")
# Note: API_KEY will be checked when the server starts, not at import time

BASE_URL = "https://api.exchangerate.host/convert"
CACHE_FILE = str(data_dir / "cache.csv")
CACHE_TTL = 3600  # 60 Minuten

app = FastAPI(title="Währungsrechner mit CSV-Cache")

# -----------------------------
# Cache: Speicher im Speicher + CSV
# -----------------------------
CACHE: dict = {}

def get_cache_key(from_currency: str, to_currency: str, amount: float) -> str:
    return f"{from_currency.upper()}-{to_currency.upper()}-{amount}"

def load_cache():
    """Lädt vorhandene Cache-Einträge aus der CSV"""
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = get_cache_key(row["from"], row["to"], float(row["amount"]))
            CACHE[key] = {
                "timestamp": float(row["timestamp"]),
                "data": {
                    "from": row["from"],
                    "to": row["to"],
                    "amount": float(row["amount"]),
                    "result": float(row["result"]),
                    "info": {
                        "rate": float(row["rate"]) if row["rate"] not in (None, '', 'None') else None
                    }
                }
            }

def save_cache():
    """Schreibt den Cache in die CSV-Datei"""
    with open(CACHE_FILE, mode="w", newline="") as f:
        fieldnames = ["from", "to", "amount", "result", "rate", "timestamp"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in CACHE.values():
            data = entry["data"]
            writer.writerow({
                "from": data["from"],
                "to": data["to"],
                "amount": data["amount"],
                "result": data["result"],
                "rate": data["info"].get("rate", None),  # <-- Fix here
                "timestamp": entry["timestamp"]
            })

def get_cache(key: str):
    item = CACHE.get(key)
    if item:
        if time.time() - item["timestamp"] < CACHE_TTL:
            # Update the timestamp to extend TTL
            item["timestamp"] = time.time()
            save_cache()
            return item["data"]
        else:
            del CACHE[key]
            save_cache()
    return None

def set_cache(key: str, value: dict):
    CACHE[key] = {"timestamp": time.time(), "data": value}
    save_cache()
    
    
def cleanup_cache():
    """Entfernt alle abgelaufenen Cache-Einträge."""
    now = time.time()
    keys_to_delete = [key for key, entry in CACHE.items() if now - entry["timestamp"] >= CACHE_TTL]
    for key in keys_to_delete:
        del CACHE[key]
    if keys_to_delete:
        save_cache()

# Lade Cache beim Start und bereinige abgelaufene Einträge
load_cache()
cleanup_cache()
# -----------------------------
# API-Endpunkt
# -----------------------------
@app.get("/convert")
async def convert(
    from_currency: str,
    to_currency: str,
    amount: str = Query(...)
):
    # Allow comma as decimal separator
    try:
        amount_float = float(amount.replace(",", "."))
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiger Betrag. Bitte Zahl mit Punkt oder Komma eingeben.")

    cache_key = get_cache_key(from_currency, to_currency, amount_float)

    # 1. Cache prüfen
    cached = get_cache(cache_key)
    if cached:
        return {"cached": True, **cached}

    # 2. API-Aufruf
    params = {
        "access_key": API_KEY,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount_float
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)

    logging.info("API response: %s", response.json())

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"API-Anfrage fehlgeschlagen: {response.status_code}")

    data = response.json()
    if not data.get("success", False):
        err = data.get("error", {})
        raise HTTPException(status_code=400, detail=f"API-Fehler: {err}")

    # Extract rate safely
    rate = None
    if "info" in data and isinstance(data["info"], dict):
        rate = data["info"].get("rate")
        if rate is None:
            rate = data["info"].get("quote")
    elif "rate" in data:
        rate = data.get("rate")

    result = {
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "amount": amount_float,
        "result": data.get("result"),
        "info": {
            "rate": rate
        }
    }

    # 3. Cache speichern
    set_cache(cache_key, result)

    return {"cached": False, **result}


def create_app() -> FastAPI:
    """Create and return the FastAPI app instance."""
    return app


def start_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the API server."""
    if not API_KEY:
        raise RuntimeError("Missing API_KEY in environment variables. Please set API_KEY in .env file.")
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
