# AGENTS.md - Quantito Pipe Development Standards

This file serves as the central reference for developers and AI agents working on **quantito-pipe**.

---

## 1. Role in the Quantito Ecosystem

**`quantito-pipe`** is the data ingestion service of the **Quantito Financial Platform**:
- Ingests market quotes (Real-time, 15-minute delayed US, EOD historical candles) from EODHD API.
- Standardizes and batches records into Google Cloud BigQuery (`quotes_real_time`, `quotes_delayed`, `quotes_eod`).
- Works alongside **`quantito`** (stateless quantitative strategy evaluation engine) and **`quantito-engine`** (experiment orchestrator, parallel contraposition, and signal dispatcher).

### Structure
```
quantito-pipe/
├── pipelines/
│   ├── __init__.py
│   ├── real_time.py            # Real-time quotes from EODHD
│   ├── delayed.py              # 15-minute delayed US quotes from EODHD
│   └── eod.py                  # End-of-Day historical quotes from EODHD
├── storage/
│   ├── __init__.py
│   └── bigquery.py             # BigQuery schema provisioning & batch inserts
├── tests/
│   ├── scripts/
│   │   └── import_container_smoke_test.sh
│   ├── test_main.py
│   ├── test_pipeline_failures.py
│   ├── test_docker_artifacts.py
│   └── test_storage.py
├── main.py                     # CLI entrypoint for job execution
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

---

## 3. Git Workflow & Branch Management

All AI agents and developers must adhere to the mandatory branch policy:
- **Dedicated Branching**: Create a new branch `<type>/<short-kebab-case-description>` (e.g., `feat/polygon-pipeline`, `fix/bigquery-batch-limit`, `docs/architecture-update`).
- **No Direct Commits**: Direct commits to `main` or `master` are strictly forbidden.
- **Commit Messages**: Plain, concise descriptions without `<type>(scope):` prefixes.
