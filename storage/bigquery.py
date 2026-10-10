import datetime
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

DELAYED_QUOTES_SCHEMA = [
    ("symbol", "STRING", "REQUIRED"),
    ("exchange", "STRING", "NULLABLE"),
    ("open", "FLOAT", "NULLABLE"),
    ("high", "FLOAT", "NULLABLE"),
    ("low", "FLOAT", "NULLABLE"),
    ("lastTradePrice", "FLOAT", "NULLABLE"),
    ("volume", "INTEGER", "NULLABLE"),
    ("timestamp", "INTEGER", "NULLABLE"),
    ("inserted_at", "TIMESTAMP", "REQUIRED"),
]

EOD_HISTORICAL_SCHEMA = [
    ("symbol", "STRING", "REQUIRED"),
    ("date", "STRING", "REQUIRED"),
    ("open", "FLOAT", "NULLABLE"),
    ("high", "FLOAT", "NULLABLE"),
    ("low", "FLOAT", "NULLABLE"),
    ("close", "FLOAT", "NULLABLE"),
    ("adjusted_close", "FLOAT", "NULLABLE"),
    ("volume", "INTEGER", "NULLABLE"),
    ("inserted_at", "TIMESTAMP", "REQUIRED"),
]

REAL_TIME_QUOTES_SCHEMA = [
    ("code", "STRING", "REQUIRED"),
    ("timestamp", "INTEGER", "NULLABLE"),
    ("gmtoffset", "INTEGER", "NULLABLE"),
    ("open", "FLOAT", "NULLABLE"),
    ("high", "FLOAT", "NULLABLE"),
    ("low", "FLOAT", "NULLABLE"),
    ("close", "FLOAT", "NULLABLE"),
    ("volume", "INTEGER", "NULLABLE"),
    ("previousClose", "FLOAT", "NULLABLE"),
    ("change", "FLOAT", "NULLABLE"),
    ("change_p", "FLOAT", "NULLABLE"),
    ("inserted_at", "TIMESTAMP", "REQUIRED"),
]


def _build_bq_schema(schema_defs: list[tuple[str, str, str]]):
    from google.cloud import bigquery

    return [
        bigquery.SchemaField(name, field_type, mode=mode) for name, field_type, mode in schema_defs
    ]


def get_bigquery_client():
    from google.cloud import bigquery

    return bigquery.Client()


def ensure_dataset(client, dataset_name: str, location: str = "US"):
    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    dataset_ref = client.dataset(dataset_name)
    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        client.create_dataset(dataset)
        logger.info("Created BigQuery dataset: %s", dataset_name)
    return dataset_ref


def ensure_table(client, dataset_ref, table_id: str, schema_defs: list[tuple[str, str, str]]):
    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    table_ref = dataset_ref.table(table_id)
    try:
        client.get_table(table_ref)
    except NotFound:
        schema = _build_bq_schema(schema_defs)
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        logger.info("Created BigQuery table: %s", table_id)
    return table_ref


class BigQueryStorage:
    """Centralized BigQuery storage manager for financial market data pipelines."""

    def __init__(self, dataset_name: str | None = None, location: str | None = None):
        self.dataset_name = dataset_name or os.getenv("BIGQUERY_DATASET")
        self.location = location or os.getenv("BIGQUERY_LOCATION", "US")

    @property
    def is_configured(self) -> bool:
        return bool(self.dataset_name)

    def store_delayed_quotes(self, data: list[dict[str, Any]]) -> None:
        if not self.is_configured:
            logger.info("BIGQUERY_DATASET is not configured. Skipping BigQuery storage.")
            return

        client = get_bigquery_client()
        dataset_ref = ensure_dataset(client, self.dataset_name, self.location)
        table_ref = ensure_table(client, dataset_ref, "delayed_quotes", DELAYED_QUOTES_SCHEMA)

        now_str = datetime.datetime.now(datetime.UTC).isoformat()
        rows = [
            {
                "symbol": row.get("symbol"),
                "exchange": row.get("exchange"),
                "open": row.get("open"),
                "high": row.get("high"),
                "low": row.get("low"),
                "lastTradePrice": row.get("lastTradePrice"),
                "volume": row.get("volume"),
                "timestamp": row.get("timestamp"),
                "inserted_at": now_str,
            }
            for row in data
        ]

        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"Errors inserting delayed quotes into BigQuery: {errors}")

        logger.info("Inserted %d delayed quotes into BigQuery.", len(rows))

    def store_eod_data(self, data: list[dict[str, Any]], chunk_size: int = 500) -> None:
        if not self.is_configured:
            logger.info("BIGQUERY_DATASET is not configured. Skipping BigQuery storage.")
            return

        client = get_bigquery_client()
        dataset_ref = ensure_dataset(client, self.dataset_name, self.location)
        table_ref = ensure_table(client, dataset_ref, "eod_historical_data", EOD_HISTORICAL_SCHEMA)

        now_str = datetime.datetime.now(datetime.UTC).isoformat()
        rows = [
            {
                "symbol": row.get("symbol"),
                "date": row.get("date"),
                "open": row.get("open"),
                "high": row.get("high"),
                "low": row.get("low"),
                "close": row.get("close"),
                "adjusted_close": row.get("adjusted_close"),
                "volume": row.get("volume"),
                "inserted_at": now_str,
            }
            for row in data
        ]

        total_inserted = 0
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            errors = client.insert_rows_json(table_ref, chunk)
            if errors:
                raise RuntimeError(
                    f"Errors inserting historical data chunk into BigQuery: {errors}"
                )
            total_inserted += len(chunk)

        logger.info("Inserted %d EOD historical data rows into BigQuery.", total_inserted)

    def store_real_time_quotes(self, data: list[dict[str, Any]]) -> None:
        if not self.is_configured:
            logger.info("BIGQUERY_DATASET is not configured. Skipping BigQuery storage.")
            return

        client = get_bigquery_client()
        dataset_ref = ensure_dataset(client, self.dataset_name, self.location)
        table_ref = ensure_table(client, dataset_ref, "real_time_quotes", REAL_TIME_QUOTES_SCHEMA)

        now_str = datetime.datetime.now(datetime.UTC).isoformat()
        rows = []
        for row in data:
            new_row = dict(row)
            new_row["inserted_at"] = now_str
            rows.append(new_row)

        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"Errors inserting real-time quotes into BigQuery: {errors}")

        logger.info("Inserted %d real-time quotes into BigQuery.", len(rows))
