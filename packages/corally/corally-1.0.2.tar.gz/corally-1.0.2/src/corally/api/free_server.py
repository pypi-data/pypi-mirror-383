import os
import time
import csv
import httpx
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    filename=str(data_dir / "api.log"),
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)

# Free API endpoints that don't require API keys
FREE_API_ENDPOINTS = [
    "https://api.exchangerate-api.com/v4/latest/",  # Free, no key required
    "https://api.fixer.io/latest?access_key=",      # Backup (requires key)
]

CACHE_FILE = str(data_dir / "cache.csv")
CACHE_TTL = 3600  # 60 minutes

app = FastAPI(title="Free Currency Converter with CSV Cache")

# Cache: Memory + CSV
CACHE: dict = {}

def get_cache_key(from_currency: str, to_currency: str, amount: float) -> str:
    return f"{from_currency.upper()}-{to_currency.upper()}-{amount}"

def load_cache():
    """Load existing cache entries from CSV"""
    if not os.path.exists(CACHE_FILE):
        return
    try:
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
    except Exception as e:
        logging.error(f"Error loading cache: {e}")

def save_cache():
    """Write cache to CSV file"""
    try:
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
                    "rate": data["info"].get("rate", None),
                    "timestamp": entry["timestamp"]
                })
    except Exception as e:
        logging.error(f"Error saving cache: {e}")

def get_cache(key: str):
    item = CACHE.get(key)
    if item:
        if time.time() - item["timestamp"] < CACHE_TTL:
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
    """Remove all expired cache entries"""
    now = time.time()
    keys_to_delete = [key for key, entry in CACHE.items() if now - entry["timestamp"] >= CACHE_TTL]
    for key in keys_to_delete:
        del CACHE[key]
    if keys_to_delete:
        save_cache()

async def get_exchange_rate(from_currency: str, to_currency: str):
    """Get exchange rate using free API"""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    logging.info(f"Getting exchange rate: {from_currency} -> {to_currency}")

    # Try the free API first
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            logging.info(f"Making request to: {url}")

            response = await client.get(url, timeout=15)
            logging.info(f"Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})
                logging.info(f"Got {len(rates)} exchange rates")

                if to_currency in rates:
                    rate = rates[to_currency]
                    logging.info(f"Exchange rate {from_currency}/{to_currency}: {rate}")
                    return rate
                else:
                    available_currencies = list(rates.keys())[:10]  # Show first 10
                    error_msg = f"Currency {to_currency} not supported. Available: {available_currencies}..."
                    logging.error(error_msg)
                    raise HTTPException(status_code=400, detail=error_msg)
            else:
                error_msg = f"External API returned status {response.status_code}: {response.text}"
                logging.error(error_msg)
                raise HTTPException(status_code=response.status_code, detail=error_msg)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except httpx.TimeoutException as e:
        error_msg = f"Request timeout: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"Network error: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Load cache on startup
load_cache()
cleanup_cache()

@app.get("/convert")
async def convert(
    from_currency: str,
    to_currency: str,
    amount: str = Query(...)
):
    logging.info(f"Convert request: {amount} {from_currency} -> {to_currency}")

    # Validate and parse amount
    try:
        amount_float = float(amount.replace(",", "."))
        if amount_float <= 0:
            raise ValueError("Amount must be positive")
    except ValueError as e:
        error_msg = f"Invalid amount '{amount}': {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # Validate currencies
    if not from_currency or not to_currency:
        raise HTTPException(status_code=400, detail="Both from_currency and to_currency are required")

    if len(from_currency) != 3 or len(to_currency) != 3:
        raise HTTPException(status_code=400, detail="Currency codes must be 3 letters (e.g., EUR, USD)")

    cache_key = get_cache_key(from_currency, to_currency, amount_float)
    logging.info(f"Cache key: {cache_key}")

    # 1. Check cache
    try:
        cached = get_cache(cache_key)
        if cached:
            logging.info("Returning cached result")
            return {"cached": True, **cached}
    except Exception as e:
        logging.warning(f"Cache lookup failed: {e}")

    # 2. Get exchange rate
    try:
        rate = await get_exchange_rate(from_currency, to_currency)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_msg = f"Failed to get exchange rate: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    # 3. Calculate result
    try:
        result_amount = amount_float * rate

        result = {
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "amount": amount_float,
            "result": round(result_amount, 2),
            "info": {
                "rate": rate
            }
        }

        logging.info(f"Conversion result: {result}")

        # 4. Save to cache
        try:
            set_cache(cache_key, result)
        except Exception as e:
            logging.warning(f"Failed to save to cache: {e}")

        return {"cached": False, **result}

    except Exception as e:
        error_msg = f"Calculation failed: {str(e)}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
async def root():
    return {"message": "Free Currency Converter API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "cache_entries": len(CACHE)}


def create_free_app() -> FastAPI:
    """Create and return the free FastAPI app instance."""
    return app


def start_free_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the free API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_free_server()
