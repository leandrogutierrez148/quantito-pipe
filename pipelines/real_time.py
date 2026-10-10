import logging
import os

import requests

from storage.bigquery import BigQueryStorage

logger = logging.getLogger(__name__)


def store_data(data):
    storage = BigQueryStorage()
    storage.store_real_time_quotes(data)


def run():
    logger.info("Starting Real-Time Quotes Pipeline.")
    api_token = os.getenv("EODHD_API_TOKEN")
    symbols_str = os.getenv("SYMBOLS", "AAPL.US,GOOGL.US")
    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]

    if not api_token:
        raise RuntimeError("EODHD_API_TOKEN is not set.")

    if not symbols:
        logger.warning("No symbols to retrieve.")
        return

    main_symbol = symbols[0]
    additional_symbols = ",".join(symbols)

    real_time_url = f"https://eodhd.com/api/real-time/{main_symbol}"
    logger.info("Retrieving real-time quotes for symbols: %s", symbols)

    try:
        response = requests.get(
            real_time_url, params={"s": additional_symbols, "api_token": api_token, "fmt": "json"}
        )
        response.raise_for_status()
        res_json = response.json()

        raw_quotes = []
        if isinstance(res_json, list):
            raw_quotes = res_json
        elif isinstance(res_json, dict):
            raw_quotes = [res_json]

    except Exception:
        raise RuntimeError("Error fetching real-time quotes.") from None

    processed_quotes = []
    for quote in raw_quotes:
        if not isinstance(quote, dict):
            continue
        code = quote.get("code")
        close = quote.get("close")
        if not code or close is None:
            logger.warning("Skipping malformed real-time quote: %s", quote)
            continue

        processed_quotes.append(quote)

    if processed_quotes:
        store_data(processed_quotes)
    else:
        logger.warning("No valid quotes to store.")


if __name__ == "__main__":
    run()
