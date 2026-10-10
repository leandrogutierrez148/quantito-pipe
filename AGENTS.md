# AGENTS.md - Quantito Pipe Development Standards

This file serves as the central reference for developers and AI agents working on **quantito-pipe**.

---

## 1. Architecture

`quantito-pipe` is a Python 3.12+ data ingestion service designed to be executed on a schedule (e.g. Cron, Cloud Run Jobs, Airflow).

### Structure
```
quantito-pipe/
├── pipelines/
│   ├── __init__.py
│   ├── real_time.py
│   ├── delayed.py
│   └── eod.py
├── storage/
│   ├── __init__.py
│   └── bigquery.py             # Centralized BigQuery client, schema definitions & batch storage
├── tests/
│   ├── scripts/
│   │   └── import_container_smoke_test.sh
│   ├── test_main.py
│   ├── test_pipeline_failures.py
│   ├── test_docker_artifacts.py
│   └── test_storage.py
├── main.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## 2. Standards & Verification

Run before every commit:
```bash
ruff check --fix .
ruff format .
ruff check . && ruff format --check .
python -m unittest discover tests
```
