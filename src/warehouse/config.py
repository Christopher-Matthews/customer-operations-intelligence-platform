"""Environment configuration for BigQuery warehouse loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


@dataclass(frozen=True)
class WarehouseConfig:
    env: str
    project_id: str
    staging_dataset: str
    raw_dataset: str


def load_warehouse_config(env: str, confirm_prod: bool = False) -> WarehouseConfig:
    if load_dotenv is not None:
        load_dotenv()
    else:
        _load_simple_dotenv()

    normalized_env = env.lower().strip()
    if normalized_env not in {"test", "prod"}:
        raise ValueError("--env must be either 'test' or 'prod'")
    if normalized_env == "prod" and not confirm_prod:
        raise ValueError("Production loads require --confirm-prod")

    project_id = _required_env("GCP_PROJECT_ID")
    prefix = "BQ_PROD" if normalized_env == "prod" else "BQ_TEST"
    staging_dataset = _required_env(f"{prefix}_STAGING_DATASET")
    raw_dataset = _required_env(f"{prefix}_RAW_DATASET")

    # google-cloud-bigquery will read GOOGLE_APPLICATION_CREDENTIALS directly.
    _required_env("GOOGLE_APPLICATION_CREDENTIALS")

    return WarehouseConfig(
        env=normalized_env,
        project_id=project_id,
        staging_dataset=staging_dataset,
        raw_dataset=raw_dataset,
    )


def get_bigquery_client(config: WarehouseConfig):
    from google.cloud import bigquery

    return bigquery.Client(project=config.project_id)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _load_simple_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
