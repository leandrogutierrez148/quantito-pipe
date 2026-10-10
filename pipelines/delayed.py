import logging
import os

import requests

from storage.bigquery import BigQueryStorage

logger = logging.getLogger(__name__)


def store_data(data):
    storage = BigQueryStorage()
    storage.store_delayed_quotes(data)


def run():
    logger.info("Starting US Delayed Quotes Pipeline.")
    api_token = os.getenv("EODHD_API_TOKEN")
    symbols_str = os.getenv("SYMBOLS", "AAPL.US,GOOGL.US")
    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]

    if not api_token:
        raise RuntimeError("EODHD_API_TOKEN is not set.")

    if not symbols:
        logger.warning("No symbols to retrieve.")
        return

    additional_symbols = ",".join(symbols)
    delayed_url = "https://eodhd.com/api/us-quote-delayed"
    logger.info("Retrieving delayed quotes for symbols: %s", symbols)

    try:
        response = requests.get(
            delayed_url, params={"s": additional_symbols, "api_token": api_token, "fmt": "json"}
        )
        response.raise_for_status()
        res_json = response.json()

        raw_quotes = []
        if isinstance(res_json, dict) and "data" in res_json:
            raw_quotes = list(res_json["data"].values())

    except Exception:
        raise RuntimeError("Error fetching US delayed quotes.") from None

    processed_quotes = []
    for quote in raw_quotes:
        if not isinstance(quote, dict):
            continue
        symbol = quote.get("symbol")
        last_trade = quote.get("lastTradePrice")
        if not symbol or last_trade is None:
            logger.warning("Skipping malformed delayed quote: %s", quote)
            continue

        processed_quotes.append(quote)

    if processed_quotes:
        store_data(processed_quotes)
    else:
        logger.warning("No valid quotes to store.")


if __name__ == "__main__":
    run()
