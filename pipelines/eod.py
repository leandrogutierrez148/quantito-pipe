import logging
import os

import requests

from storage.bigquery import BigQueryStorage

logger = logging.getLogger(__name__)


def store_data(data):
    storage = BigQueryStorage()
    storage.store_eod_data(data)


def run():
    logger.info("Starting EOD Historical Data Pipeline.")
    api_token = os.getenv("EODHD_API_TOKEN")
    symbols_str = os.getenv("SYMBOLS", "AAPL.US,GOOGL.US")
    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]

    if not api_token:
        raise RuntimeError("EODHD_API_TOKEN is not set.")

    if not symbols:
        logger.warning("No symbols to retrieve.")
        return

    raw_data = []
    for symbol in symbols:
        eod_url = f"https://eodhd.com/api/eod/{symbol}"
        logger.info("Retrieving EOD Historical Data for symbol: %s", symbol)

        try:
            response = requests.get(eod_url, params={"api_token": api_token, "fmt": "json"})
            response.raise_for_status()
            symbol_data = response.json()

            if isinstance(symbol_data, list):
                for entry in symbol_data:
                    if isinstance(entry, dict):
                        raw_data.append({**entry, "symbol": symbol})

        except Exception:
            raise RuntimeError(f"Error fetching EOD historical data for symbol {symbol}.") from None

    processed_data = []
    for entry in raw_data:
        symbol = entry.get("symbol")
        date = entry.get("date")
        if not symbol or not date:
            logger.warning("Skipping malformed EOD entry: %s", entry)
            continue
        processed_data.append(entry)

    processed_data.sort(key=lambda x: (x["symbol"], x["date"]))

    if processed_data:
        store_data(processed_data)
    else:
        logger.warning("No valid EOD historical data to store.")


if __name__ == "__main__":
    run()
