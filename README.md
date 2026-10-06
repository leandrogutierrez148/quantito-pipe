# Quantito Pipe (`quantito-pipe`)

`quantito-pipe` is the dedicated data ingestion and collection service for the Quantito financial platform. It fetches market quotes (real-time, delayed, and End-of-Day historical) from financial APIs (EODHD) and persists them into Google Cloud BigQuery.

---

## Features

- **Real-Time Quotes Pipeline**: Ingests real-time market data quotes.
- **US Delayed Quotes Pipeline**: Fetches 15-minute delayed US market quotes.
- **EOD Historical Data Pipeline**: Downloads end-of-day candles/historical prices.
- **BigQuery Persistence**: Automatically manages dataset/table creation and batch loading into BigQuery.
- **Robust CLI Orchestrator**: Configurable pipeline execution via CLI flags or environment variables.

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `EODHD_API_TOKEN` | EODHD API authentication token | *(Required)* |
| `BIGQUERY_DATASET` | BigQuery dataset to store data | *(Optional)* |
| `BIGQUERY_LOCATION` | Region for BigQuery dataset creation | `US` |
| `SYMBOLS` | Comma-separated list of ticker symbols | `AAPL.US,GOOGL.US` |
| `PIPELINES` | Comma-separated pipelines to run (`real_time`, `delayed`, `eod`) | `real_time,delayed,eod` |

---

## Local Development

```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run linter and formatting
ruff check . && ruff format --check .

# Run test suite
python -m unittest discover tests

# Run pipelines
export EODHD_API_TOKEN="your_token"
python main.py --pipelines real_time,delayed,eod
```

---

## Docker Execution

```bash
# Build Docker image
docker build -t quantito-pipe:latest .

# Run container
docker run --rm \
  -e EODHD_API_TOKEN="your_token" \
  -e BIGQUERY_DATASET="market_data" \
  -e PIPELINES="real_time,delayed,eod" \
  quantito-pipe:latest
```
